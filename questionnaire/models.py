from django.db import models
from accounts.models import CustomUser


class QuestionnaireResponse(models.Model):
    """Stores one questionnaire submission for a user."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='responses')

    # Parent questionnaire answers (Likert 1-5)
    pq1 = models.PositiveSmallIntegerField(help_text="Understand child's point of view")
    pq2 = models.PositiveSmallIntegerField(help_text="Pay full attention when child shares problems")
    pq3 = models.PositiveSmallIntegerField(help_text="Express emotions clearly and respectfully")
    pq4 = models.PositiveSmallIntegerField(help_text="Control anger/frustration during conversations")
    pq5 = models.PositiveSmallIntegerField(help_text="Spend quality time talking daily")
    pq6 = models.PositiveSmallIntegerField(help_text="Praise or encourage child's efforts")
    pq7 = models.PositiveSmallIntegerField(help_text="Listen without interrupting")
    pq8 = models.PositiveSmallIntegerField(help_text="Discuss daily activities or school events")
    pq9 = models.PositiveSmallIntegerField(help_text="Set clear, consistent boundaries respectfully")
    pq10 = models.PositiveSmallIntegerField(help_text="Apologize when wrong")

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'questionnaire_responses'
        ordering = ['-submitted_at']

    def as_feature_list(self):
        """Return answers as ordered numeric list for ML inference."""
        return [self.pq1, self.pq2, self.pq3, self.pq4, self.pq5,
                self.pq6, self.pq7, self.pq8, self.pq9, self.pq10]

    def __str__(self):
        return f"Response by {self.user.username} at {self.submitted_at:%Y-%m-%d %H:%M}"


class PredictionResult(models.Model):
    """Stores the ML prediction result for a questionnaire response."""
    CATEGORY_CHOICES = [
        ('Strong', 'Strong'),
        ('Moderate', 'Moderate'),
        ('Weak', 'Weak'),
    ]
    response = models.OneToOneField(
        QuestionnaireResponse, on_delete=models.CASCADE, related_name='result'
    )
    score = models.FloatField(help_text="Score between 1 and 3")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    predicted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prediction_results'
        ordering = ['-predicted_at']

    def __str__(self):
        return f"{self.category} ({self.score:.2f}) — {self.response.user.username}"


class Recommendation(models.Model):
    """Actionable recommendation linked to a prediction result."""
    result = models.ForeignKey(PredictionResult, on_delete=models.CASCADE, related_name='recommendations')
    text = models.TextField()

    class Meta:
        db_table = 'recommendations'

    def __str__(self):
        return self.text[:60]
