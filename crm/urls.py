from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Workers
    path('workers/', views.worker_list, name='worker_list'),
    path('workers/<int:pk>/', views.worker_detail, name='worker_detail'),
    path('workers/new/', views.worker_create, name='worker_create'),
    path('workers/<int:pk>/edit/', views.worker_update, name='worker_update'),
    path('workers/<int:pk>/delete/', views.worker_delete, name='worker_delete'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/new/', views.order_create, name='order_create'),
    path('orders/<int:pk>/edit/', views.order_update, name='order_update'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),

    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/record/', views.attendance_bulk_create, name='attendance_bulk_create'),
]