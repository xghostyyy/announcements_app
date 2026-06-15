from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.authtoken.views import ObtainAuthToken

class CustomObtainAuthToken(ObtainAuthToken):
    authentication_classes = []

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('main.urls')),
    path('api/v1/', include('main.urls')),
    path('api/v2/', include('APIv2.urls',)),
    path('', auth_views.LoginView.as_view(template_name='main/login.html', next_page='auth/'), name='login'),
    path('api/api-token-auth/', CustomObtainAuthToken.as_view(), name='api_token_auth'), # a9d9e8f3815852497e564f536814f540bf01d421
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)