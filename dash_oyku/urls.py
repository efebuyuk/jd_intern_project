from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.startapp),
    url('language_cell_count/', views.change_features, name='change_features'),
    url('language_func/', views.change_language, name='change_language')
]