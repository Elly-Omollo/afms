from django.urls import path
from . import views

app_name = "userauth"

urlpatterns = [
    path('login/', views.loginView, name= 'Login View'),
    path('logout/', views.logoutView, name= 'Logout View'),
    path('signup/', views.signupView, name= 'Signup View'),
    path('verification/', views.verify_otp, name= 'OTP View'),

    # farm owner pages dashboard pages 
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.products, name='products'),
    path('calender/', views.calender, name='calender'),
    path('profile/', views.profile, name='profile'),
]

