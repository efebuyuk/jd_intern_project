"""jd_intern_project URL Configuration

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
from django.urls import include, path

from yigit import views
from mainpage import views


urlpatterns = [
    path('', include('mainpage.urls')),
    path('yigit', include('yigit.urls')),
    path('admin/', admin.site.urls),
    path('', views.index, name='index.html'),

    path('signup', views.signup, name='signup.html'),
    path('login', views.loginPage, name='login.html'),
    path('logout', views.logoutUser, name='logout.html'),
    path('logged_home', views.logged_home, name='logged_home.html'),
    path('dash_oyku/', include('dash_oyku.urls')),
    path('dash_berkay/', include('dash_berkay.urls'))

]
