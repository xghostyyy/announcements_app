from django.urls import path
from main import views

urlpatterns = [
    path('', views.trade_list, name='trade_list'),
]
