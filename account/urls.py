from django.urls import path
from . import views

urlpatterns = [
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('logout',views.logout,name='logout'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('',views.dashboard,name='account'),
    path('forgot-password',views.forgot_password,name='forgot_password'),
    path('reset-password-validation/<uidb64>/<token>',views.reset_password_validation,name='reset_password_validation'),
    path('reset-password',views.reset_password,name='reset_password'),
    path('activate/<uidb64>/<token>',views.activate,name='activate'),
    path('my-orders',views.my_orders,name='my_orders')
]