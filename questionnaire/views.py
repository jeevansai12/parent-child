from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import QuestionnaireResponse, PredictionResult, Recommendation
from .serializers import QuestionnaireResponseSerializer, PredictionResultSerializer
from ml_engine.predict import run_prediction


# ── RECOMMENDATION LOGIC ────────────────────────────────────────────────────
STRONG_MESSAGES = [
    "🌟 Excellent! Your communication with your child is strong and healthy.",
    "Keep nurturing open dialogue — you are doing a fantastic job!",
    "Your child feels heard, valued, and supported. Maintain this connection.",
]

IMPROVEMENT_SUGGESTIONS = {
    'listening': "📢 Improve active listening skills — give your full attention without distractions.",
    'daily_time': "⏱️ Increase daily communication time with your child (aim for at least 15–20 minutes/day).",
    'emotional': "💬 Practice expressing emotions clearly and calmly to model healthy communication.",
    'interruptions': "🤫 Reduce interruptions — let your child finish speaking before responding.",
    'empathy': "❤️ Show more empathy by acknowledging your child's feelings before offering solutions.",
    'praise': "🏅 Celebrate small achievements — praise and encouragement build confidence.",
    'boundaries': "📏 Set consistent, respectful boundaries and explain the reasoning to your child.",
    'apology': "🙏 Modeling accountability by apologizing when wrong teaches your child integrity.",
}


def _build_recommendations(category: str, answers: list) -> list:
    """Generate context-aware recommendation texts."""
    recs = []
    if category == 'Strong':
        recs.extend(STRONG_MESSAGES)
        return recs

    # Always add core suggestions for Moderate/Weak
    recs.append(IMPROVEMENT_SUGGESTIONS['daily_time'])
    recs.append(IMPROVEMENT_SUGGESTIONS['emotional'])

    # Targeted suggestions based on lowest-scoring answers
    indexed = list(enumerate(answers, start=1))
    indexed.sort(key=lambda x: x[1])  # lowest first

    weak_questions = [q for q, score in indexed if score <= 2]

    if 2 in weak_questions or 7 in weak_questions:   # Q2/Q7 = listening / interrupting
        recs.append(IMPROVEMENT_SUGGESTIONS['listening'])
        recs.append(IMPROVEMENT_SUGGESTIONS['interruptions'])
    if 3 in weak_questions or 4 in weak_questions:   # Q3/Q4 = emotions / anger
        recs.append(IMPROVEMENT_SUGGESTIONS['emotional'])
    if 6 in weak_questions:                          # Q6 = praise
        recs.append(IMPROVEMENT_SUGGESTIONS['praise'])
    if 9 in weak_questions:                          # Q9 = boundaries
        recs.append(IMPROVEMENT_SUGGESTIONS['boundaries'])
    if 10 in weak_questions:                         # Q10 = apology
        recs.append(IMPROVEMENT_SUGGESTIONS['apology'])
    if 1 in weak_questions:                          # Q1 = empathy
        recs.append(IMPROVEMENT_SUGGESTIONS['empathy'])

    return list(dict.fromkeys(recs))  # deduplicate while preserving order


def _create_result(response: QuestionnaireResponse) -> PredictionResult:
    """Run ML prediction and save result + recommendations."""
    score, category = run_prediction(response.as_feature_list())
    result = PredictionResult.objects.create(
        response=response, score=score, category=category
    )
    texts = _build_recommendations(category, response.as_feature_list())
    for text in texts:
        Recommendation.objects.create(result=result, text=text)
    return result


# ── QUESTION DEFINITIONS ─────────────────────────────────────────────────────
_LIKERT_CHOICES = [
    {'value': 1, 'emoji': '😞'},
    {'value': 2, 'emoji': '😕'},
    {'value': 3, 'emoji': '😐'},
    {'value': 4, 'emoji': '😊'},
    {'value': 5, 'emoji': '🌟'},
]

QUESTIONS_DATA = [
    {'text': 'Do you try to understand your child\'s point of view before responding?', 'choices': _LIKERT_CHOICES},
    {'text': 'Do you pay full attention when your child shares problems or feelings?', 'choices': _LIKERT_CHOICES},
    {'text': 'Do you express your emotions clearly and respectfully to your child?', 'choices': _LIKERT_CHOICES},
    {'text': 'Do you control your anger or frustration during conversations with your child?', 'choices': _LIKERT_CHOICES},
    {'text': 'Do you spend quality time talking with your child daily?', 'choices': _LIKERT_CHOICES},
    {'text': 'Do you praise or encourage your child\'s efforts and achievements?', 'choices': _LIKERT_CHOICES},
    {'text': 'Do you listen without interrupting when your child is speaking?', 'choices': _LIKERT_CHOICES},
    {'text': 'Do you discuss daily activities or school events with your child?', 'choices': _LIKERT_CHOICES},
    {'text': 'Do you set clear and consistent boundaries while remaining respectful?', 'choices': _LIKERT_CHOICES},
    {'text': 'Do you apologize to your child when you are wrong?', 'choices': _LIKERT_CHOICES},
]


# ── HTML VIEWS ──────────────────────────────────────────────────────────────
@login_required
def questionnaire_page(request):
    if request.method == 'POST':
        serializer = QuestionnaireResponseSerializer(data=request.POST)
        if serializer.is_valid():
            response = serializer.save(user=request.user)
            result = _create_result(response)
            return redirect('results', result_id=result.id)
        else:
            messages.error(request, "Please answer all questions with a value between 1 and 5.")
    return render(request, 'questionnaire/questionnaire.html', {
        'questions_data': QUESTIONS_DATA,
    })


@login_required
def results_page(request, result_id):
    result = get_object_or_404(PredictionResult, id=result_id, response__user=request.user)
    return render(request, 'questionnaire/results.html', {'result': result})


@login_required
def history_page(request):
    results = PredictionResult.objects.filter(
        response__user=request.user
    ).select_related('response').prefetch_related('recommendations')
    return render(request, 'questionnaire/history.html', {'results': results})


# ── REST API ─────────────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_submit_questionnaire(request):
    serializer = QuestionnaireResponseSerializer(data=request.data)
    if serializer.is_valid():
        response = serializer.save(user=request.user)
        result = _create_result(response)
        result_serializer = PredictionResultSerializer(result)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_predict(request):
    """Return the latest prediction result for the current user."""
    try:
        latest = PredictionResult.objects.filter(
            response__user=request.user
        ).select_related('response').prefetch_related('recommendations').latest('predicted_at')
        return Response(PredictionResultSerializer(latest).data)
    except PredictionResult.DoesNotExist:
        return Response({'detail': 'No predictions found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_results_history(request):
    results = PredictionResult.objects.filter(
        response__user=request.user
    ).select_related('response').prefetch_related('recommendations')
    return Response(PredictionResultSerializer(results, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_recommendations(request):
    """Return recommendations from the latest prediction."""
    try:
        latest = PredictionResult.objects.filter(
            response__user=request.user
        ).prefetch_related('recommendations').latest('predicted_at')
        recs = list(latest.recommendations.values_list('text', flat=True))
        return Response({'category': latest.category, 'score': latest.score, 'recommendations': recs})
    except PredictionResult.DoesNotExist:
        return Response({'detail': 'No recommendations found.'}, status=status.HTTP_404_NOT_FOUND)
