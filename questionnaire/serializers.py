from rest_framework import serializers
from .models import QuestionnaireResponse, PredictionResult, Recommendation


LIKERT_RANGE = range(1, 6)


def validate_likert(value):
    if value not in LIKERT_RANGE:
        raise serializers.ValidationError("Answer must be between 1 and 5.")
    return value


class QuestionnaireResponseSerializer(serializers.ModelSerializer):
    pq1 = serializers.IntegerField(validators=[validate_likert])
    pq2 = serializers.IntegerField(validators=[validate_likert])
    pq3 = serializers.IntegerField(validators=[validate_likert])
    pq4 = serializers.IntegerField(validators=[validate_likert])
    pq5 = serializers.IntegerField(validators=[validate_likert])
    pq6 = serializers.IntegerField(validators=[validate_likert])
    pq7 = serializers.IntegerField(validators=[validate_likert])
    pq8 = serializers.IntegerField(validators=[validate_likert])
    pq9 = serializers.IntegerField(validators=[validate_likert])
    pq10 = serializers.IntegerField(validators=[validate_likert])

    class Meta:
        model = QuestionnaireResponse
        fields = ['id', 'pq1', 'pq2', 'pq3', 'pq4', 'pq5',
                  'pq6', 'pq7', 'pq8', 'pq9', 'pq10', 'submitted_at']
        read_only_fields = ['id', 'submitted_at']


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ['id', 'text']


class PredictionResultSerializer(serializers.ModelSerializer):
    recommendations = RecommendationSerializer(many=True, read_only=True)
    submitted_at = serializers.DateTimeField(source='response.submitted_at', read_only=True)

    class Meta:
        model = PredictionResult
        fields = ['id', 'score', 'category', 'predicted_at', 'submitted_at', 'recommendations']
