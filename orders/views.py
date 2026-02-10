import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cart.cart import Cart
from .models import Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY


@require_POST
def create_checkout_session(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_detail')

    line_items = []
    for item in cart:
        # KRW is zero-decimal currency — pass price as integer directly
        line_items.append({
            'price_data': {
                'currency': 'krw',
                'product_data': {
                    'name': item['product'].name,
                },
                'unit_amount': int(item['price']),
            },
            'quantity': item['quantity'],
        })

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        shipping_address_collection={
            'allowed_countries': ['KR', 'US', 'JP', 'CN', 'GB', 'DE', 'FR'],
        },
        customer_email=request.user.email if request.user.is_authenticated else None,
        success_url=request.build_absolute_uri('/orders/success/') + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri('/orders/cancel/'),
        metadata={
            'user_id': str(request.user.id) if request.user.is_authenticated else '',
        },
    )

    return redirect(checkout_session.url, code=303)


def checkout_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('home')

    # Prevent duplicate order creation
    existing = Order.objects.filter(stripe_checkout_session_id=session_id).first()
    if existing:
        return render(request, 'orders/order_confirmation.html', {'order': existing})

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        messages.error(request, 'Could not verify payment session.')
        return redirect('home')

    if session.payment_status != 'paid':
        messages.error(request, 'Payment not completed.')
        return redirect('cart_detail')

    cart = Cart(request)

    # Build order from session
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        email=session.customer_details.email or '',
        stripe_checkout_session_id=session_id,
        stripe_payment_intent_id=session.payment_intent or '',
        status='paid',
        total=int(session.amount_total),
    )

    # Save shipping info
    if session.shipping_details:
        addr = session.shipping_details.address or {}
        order.shipping_name = session.shipping_details.name or ''
        order.shipping_address_line1 = addr.get('line1', '')
        order.shipping_address_line2 = addr.get('line2', '') or ''
        order.shipping_city = addr.get('city', '')
        order.shipping_state = addr.get('state', '') or ''
        order.shipping_postal_code = addr.get('postal_code', '')
        order.shipping_country = addr.get('country', '')
        order.save()

    # Create order items from cart
    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            product_name=item['product'].name,
            product_price=int(item['price']),
            quantity=item['quantity'],
        )

    cart.clear()
    return render(request, 'orders/order_confirmation.html', {'order': order})


def checkout_cancel(request):
    messages.info(request, 'Checkout was cancelled.')
    return redirect('cart_detail')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).exclude(status='pending')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@staff_member_required
def manage_orders(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        if order_id and new_status:
            order = get_object_or_404(Order, id=order_id)
            order.status = new_status
            order.save()
            messages.success(request, f'Order {order.order_number} updated to {new_status}.')
        return redirect('manage_orders')

    orders = Order.objects.exclude(status='pending')
    return render(request, 'orders/manage_orders.html', {'orders': orders})
