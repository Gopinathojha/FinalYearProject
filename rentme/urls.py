from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('customer/login/', views.customer_login_signup, name='customer_login_signup'),
    path('seller/login/', views.seller_login_signup, name='seller_login_signup'),
    path('customer/landing/', views.customer_landing, name='customer_landing'),
    path('seller/landing/', views.seller_landing, name='seller_landing'),
    path('properties/all/', views.all_properties, name='all_properties'),
    path('property/<int:property_id>/', views.property_detail, name='property_detail'),
    path('property/delete/<int:property_id>/', views.delete_property, name='delete_property'),
    path('logout/', views.user_logout, name='logout'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
]