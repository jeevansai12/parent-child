from django.urls import path
from . import views

urlpatterns = [
    # HTML pages
    path('questionnaire/', views.questionnaire_page, name='questionnaire'),
    path('results/<int:result_id>/', views.results_page, name='results'),
    path('history/', views.history_page, name='history'),

    # REST API
    path('api/submit-questionnaire/', views.api_submit_questionnaire, name='api_submit_questionnaire'),
    path('api/predict/', views.api_predict, name='api_predict'),
    path('api/results-history/', views.api_results_history, name='api_results_history'),
    path('api/recommendations/', views.api_recommendations, name='api_recommendations'),
]
