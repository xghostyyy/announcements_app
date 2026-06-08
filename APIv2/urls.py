from django.urls import path
from APIv2 import views

urlpatterns = [
    path('trades/', views.AnnouncementList.as_view(), 
         name='announcement_list'),
]
