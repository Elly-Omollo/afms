from django.urls import path
from . import views

app_name = "afms_app"

urlpatterns = [
    path('', views.home, name='Home page'),
    path('reviews/', views.Reviews, name='add review'),
    path('review_listing/', views.review_listing, name='review_list'),
    path('reviews/<int:review_id>/add_comment/', views.add_comment, name='add_comment'),
    path('reviews/like-dislike/', views.like_dislike_review, name='like_dislike'),

    path('products/', views.Products, name='products page'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),


    # prooducts listing urls
    path('products/crops/', views.crops, name='crops'),
    path('products/livestock/', views.livestock, name='livestock'),
    path('products/poultry/', views.poultry, name='poultry'),


    path('get-activities/', views.get_activities, name='get_activities'),
    path('add-activity/', views.add_activity, name='add_activity'),
    path('get_reviews/', views.get_reviews, name='get_reviews'),
    path('place/<int:product_id>/', views.place_order, name='place_order'),
    path('cancel/<int:product_id>/', views.cancel_order, name='cancel_order'),





    path('customer_profile', views.customer_profile, name='Customer Profile')
]