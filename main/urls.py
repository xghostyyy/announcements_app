from django.urls import path
from main import views

urlpatterns = [
    path('auth/', views.index, name='index'),
    path('trades/', views.announcement_list, name='announcement_list'),
    path('trades/<int:id>/', views.announcement_data, name='announcement_data'),
    path('trades/<int:id>/images/', views.add_image, name='add_image'),
    path('trades/<int:id>/images/<int:image_id>/', views.delete_image, name='delete_image'),
]
