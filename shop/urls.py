from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list_view, name='product_list'),
    path('manage/', views.manage_dashboard_view, name='manage_dashboard'),
    path('manage/create/', views.manage_create_view, name='manage_create'),
    path('manage/<int:pk>/edit/', views.manage_edit_view, name='manage_edit'),
    path('manage/<int:pk>/delete/', views.manage_delete_view, name='manage_delete'),
    path('manage/category/add/', views.manage_category_add_view, name='manage_category_add'),
    path('manage/category/<int:pk>/delete/', views.manage_category_delete_view, name='manage_category_delete'),
    path('manage/image/<int:pk>/delete/', views.manage_image_delete_view, name='manage_image_delete'),
    path('manage/content-image/<int:pk>/delete/', views.manage_content_image_delete_view, name='manage_content_image_delete'),
    path('manage/banner/create/', views.manage_banner_create_view, name='manage_banner_create'),
    path('manage/banner/<int:pk>/edit/', views.manage_banner_edit_view, name='manage_banner_edit'),
    path('manage/banner/<int:pk>/delete/', views.manage_banner_delete_view, name='manage_banner_delete'),
    path('manage/popup/create/', views.manage_popup_create_view, name='manage_popup_create'),
    path('manage/popup/<int:pk>/edit/', views.manage_popup_edit_view, name='manage_popup_edit'),
    path('manage/popup/<int:pk>/delete/', views.manage_popup_delete_view, name='manage_popup_delete'),
    path('<slug:slug>/', views.product_detail_view, name='product_detail'),
]
