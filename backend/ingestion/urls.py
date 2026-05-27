from django.urls import path
from .views import (
    SAPUploadView, UtilityUploadView, TravelUploadView,
    NormalizeView, RecordsListView,
    ApproveRecordView, RejectRecordView, DashboardStatsView
)

urlpatterns = [
    # Upload APIs
    path('upload/sap/', SAPUploadView.as_view()),
    path('upload/utility/', UtilityUploadView.as_view()),
    path('upload/travel/', TravelUploadView.as_view()),

    # Normalization
    path('normalize/', NormalizeView.as_view()),

    # Review APIs
    path('records/', RecordsListView.as_view()),
    path('records/<int:pk>/approve/', ApproveRecordView.as_view()),
    path('records/<int:pk>/reject/', RejectRecordView.as_view()),

    # Dashboard
    path('dashboard/stats/', DashboardStatsView.as_view()),
]