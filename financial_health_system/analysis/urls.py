from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_pnl, name="upload_pnl"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
