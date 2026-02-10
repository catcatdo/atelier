from .models import MenuItem


def menu_context(request):
    active_items = MenuItem.objects.filter(is_active=True)
    return {
        'header_menu': active_items.filter(location='header'),
        'footer_nav_menu': active_items.filter(location='footer_nav'),
        'footer_account_menu': active_items.filter(location='footer_account'),
    }
