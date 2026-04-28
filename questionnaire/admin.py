from django.contrib import admin
from .models import QuestionnaireResponse, PredictionResult, Recommendation


@admin.register(QuestionnaireResponse)
class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'submitted_at')
    list_filter = ('submitted_at',)
    readonly_fields = ('submitted_at',)


@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = ('response', 'score', 'category', 'predicted_at')
    list_filter = ('category', 'predicted_at')
    readonly_fields = ('predicted_at',)


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('result', 'text')
    list_filter = ('result__category',)
