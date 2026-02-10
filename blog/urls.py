from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list_view, name='post_list'),
    path('<slug:slug>/', views.post_detail_view, name='post_detail'),
]
