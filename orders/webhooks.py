import stripe
from django.conf import settings
from django.db.models import F
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Order, OrderItem
from shop.models import Product

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        _handle_checkout_completed(session)

    return HttpResponse(status=200)


def _handle_checkout_completed(session):
    session_id = session['id']

    order = Order.objects.filter(stripe_checkout_session_id=session_id).first()
    if not order:
        # Order may have been created in success view; create if missing
        user_id = session.get('metadata', {}).get('user_id')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = None
        if user_id:
            user = User.objects.filter(id=user_id).first()

        order = Order.objects.create(
            user=user,
            email=session.get('customer_details', {}).get('email', ''),
            stripe_checkout_session_id=session_id,
            stripe_payment_intent_id=session.get('payment_intent', ''),
            status='pending',
            total=int(session.get('amount_total', 0)),
        )

    # Idempotency: skip if already paid
    if order.status == 'paid':
        return

    order.status = 'paid'
    order.stripe_payment_intent_id = session.get('payment_intent', '') or order.stripe_payment_intent_id

    # Save shipping info
    shipping = session.get('shipping_details')
    if shipping:
        addr = shipping.get('address', {})
        order.shipping_name = shipping.get('name', '')
        order.shipping_address_line1 = addr.get('line1', '')
        order.shipping_address_line2 = addr.get('line2', '') or ''
        order.shipping_city = addr.get('city', '')
        order.shipping_state = addr.get('state', '') or ''
        order.shipping_postal_code = addr.get('postal_code', '')
        order.shipping_country = addr.get('country', '')

    order.save()

    # Deduct stock with F() and stock__gte guard
    for item in order.items.all():
        if item.product_id:
            updated = Product.objects.filter(
                id=item.product_id,
                stock__gte=item.quantity,
            ).update(stock=F('stock') - item.quantity)
            if not updated:
                # Stock insufficient — log but don't fail
                pass
