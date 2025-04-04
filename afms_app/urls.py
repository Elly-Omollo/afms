from django.urls import path
from . import views

app_name = "afms_app"

urlpatterns = [
    path('', views.home, name='Home page'),
    path('reviews/', views.Reviews, name='add review'),
    path('products/', views.Products, name='products page')
]