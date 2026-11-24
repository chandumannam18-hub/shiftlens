from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/weekly/", views.report_api, name="report-api"),
]
