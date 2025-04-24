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
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('products/', views.products, name='products'),
    path('calender/', views.calender, name='calender'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('customer/order/', views.customer_oders, name='customer_oders'),

    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('vehicle/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('vehicle/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),
    path('order/<int:pk>/detail/', views.order_detail, name='order_detail'),
    path('review/<int:pk>/detail/', views.review_detail, name='review_detail'),
    path('review/<int:pk>/approve/', views.review_approve, name='review_approve'),
    path('review/<int:pk>/delete/', views.review_delete, name='review_delete'),
    path('orders/', views.order_list, name='order_list'),

    path('contact/', views.contact, name='Contact Us')
]

