"""
URL configuration for voice_analyzer1_gem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from analyzer1 import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),  # Uncomment if admin site is needed
    path('index/', views.index, name='index'),  # Redirect to the index page
    path('', views.user_login, name='login'),  # Use custom login view
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Logout functionality
    path('signup/', views.signup, name='signup'),  # Signup page
    path('transcribe/', views.transcribe, name='transcribe'),  # Transcription functionality
    path('history/', views.history, name='history'),  # Transcription history
    path('analysis-report/', views.analysis_report, name='analysis_report'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)