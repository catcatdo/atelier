from django.urls import path
from . import views, webhooks

urlpatterns = [
    path('checkout/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.checkout_success, name='checkout_success'),
    path('cancel/', views.checkout_cancel, name='checkout_cancel'),
    path('history/', views.order_history, name='order_history'),
    path('<uuid:order_number>/', views.order_detail, name='order_detail'),
    path('manage/', views.manage_orders, name='manage_orders'),
    path('webhook/stripe/', webhooks.stripe_webhook, name='stripe_webhook'),
]
