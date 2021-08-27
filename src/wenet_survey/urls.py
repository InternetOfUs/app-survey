"""wenet_survey URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path

from authentication.views.home import HomeView
from authentication.views.logout import LogoutView
from authentication.views.oauth import OauthView
from survey.views.survey import SurveyView
from ws.views.survey import SurveyEventView


urlpatterns = [
    path(settings.BASE_URL, HomeView.as_view()),
    path(f"{settings.BASE_URL}oauth/", OauthView.as_view()),
    path(f"{settings.BASE_URL}logout/", LogoutView.as_view()),
    path(f"{settings.BASE_URL}survey/", SurveyView.as_view()),
    path(f"{settings.BASE_URL}survey/event/", SurveyEventView.as_view()),
    path(f"{settings.BASE_URL}admin/", admin.site.urls),
]
