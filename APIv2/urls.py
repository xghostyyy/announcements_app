from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('trades/', views.AnnouncementList.as_view(), 
         name='announcement_list'),
    path('trades/<int:id>/', csrf_exempt(views.AnnouncementData.as_view()),
         name='announcement_data')
]
