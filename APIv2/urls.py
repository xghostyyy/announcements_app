from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
     path('trades/', views.AnnouncementList.as_view(), 
         name='announcement_list'),
     path('trades/<int:id>/', csrf_exempt(views.AnnouncementData.as_view()),
         name='announcement_data'),
     path('trades/<int:id>/images/', csrf_exempt(views.AddImage.as_view()),
          name='add_image'),
     path('trades/<int:id>/images/<int:image_id>/', 
          csrf_exempt(views.DeleteImage.as_view()), name='delete_image'),
]
