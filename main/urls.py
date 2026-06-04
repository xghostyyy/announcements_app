from django.urls import path
from main import views

urlpatterns = [
    path('', views.announcement_list, name='announcement_list'),
]
