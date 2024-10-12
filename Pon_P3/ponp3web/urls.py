"""
URL configuration for Pon_P3 project.

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
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('input/',views.input,name='input_prediction'),
    path('input_genomic/', views.input_genomic, name='input_genomic_variation'),  # New genomic variation input
    path('input_transcript/', views.input_transcript, name='input_transcript_variation'),  # New transcript variation input
    path('disclaimer/',views.disclaimer,name='disclaimer'),
    path('uppload/',views.upload,name='upload'),
    
]
