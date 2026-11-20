# transcriber/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page route
    path('api/transcribe/', views.transcribe_audio, name='transcribe'),  # Transcribe API route
    path("api/summarize/", views.summarize_text, name="summarize"), # Summarize API route
]
