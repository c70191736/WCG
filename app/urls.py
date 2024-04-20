from django.urls import path
from .import views

from django.conf import settings 
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('generate_codes/', views.generate_codes, name='generate_codes'),
    path('error_page/', views.error_page, name='error_page'),
]