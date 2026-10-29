from django.contrib import admin
from django.urls import path
from notes import views

urlpatterns = [
    path("", views.home),
    path("config", views.config),
    path("healthz", views.health),
    path("api/csrf", views.csrf),
    path("api/login", views.login),
    path("api/logout", views.logout),
    path("api/me", views.me),
    path("api/notes", views.notes),
    path("api/notes/<int:identifier>", views.detail),
    path("admin/", admin.site.urls),
]
