from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list_view, name='product_list'),
    path('manage/', views.manage_dashboard_view, name='manage_dashboard'),
    path('manage/create/', views.manage_create_view, name='manage_create'),
    path('manage/<int:pk>/edit/', views.manage_edit_view, name='manage_edit'),
    path('manage/<int:pk>/delete/', views.manage_delete_view, name='manage_delete'),
    path('<slug:slug>/', views.product_detail_view, name='product_detail'),
]
