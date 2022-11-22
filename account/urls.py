from django.urls import path
from . import views

urlpatterns = [
    path('register',views.register,name='register'),
    path('loging',views.loging,name='loging'),
    path('logout',views.logout,name='logout'),
]