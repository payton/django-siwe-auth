from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/save", views.save, name="save"),
    path("api/me", views.me, name="me"),
    path("api/shared", views.shared, name="shared"),
]
