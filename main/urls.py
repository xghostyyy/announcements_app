from django.urls import path
from main import views

urlpatterns = [
    path('auth/', views.index, name='index'),
    path('api/v1/trades/', views.announcement_list, name='announcement_list'),
    path('api/v1/trades/<int:id>/', views.announcement_data, name='announcement_data'),
    path('api/v1/trades/<int:id>/images/', views.add_image, name='add_image'),
    path('api/v1/trades/<int:id>/images/<int:image_id>/', views.delete_image, name='delete_image'),
]
