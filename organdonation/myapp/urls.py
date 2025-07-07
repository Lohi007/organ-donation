"""organdonation URL Configuration

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
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home', views.index, name='index'),
    path('login', views.login, name='login'),
    path('homepage', views.homepage, name='homepage'),
    path('register', views.register, name='register'),
    path('registerrept', views.registerrept, name='registerrept'),
    path('requestorgan', views.requestorgan, name='requestorgan'),
    path('vieworgan', views.vieworgan, name='vieworgan'),
    path('about_us', views.about_us, name='about_us'),
    path('donor/<str:id>/', views.donor_detail, name='donor_detail'),
    path('', views.otp_process, name='otp_process'),
]
