from .models import MenuItem, SiteSetting


def menu_context(request):
    active_items = MenuItem.objects.filter(is_active=True)
    try:
        site_settings = SiteSetting.objects.first()
    except Exception:
        site_settings = None
    header_items = active_items.filter(location='header')
    return {
        'header_menu': header_items,
        'footer_nav_menu': header_items,
        'footer_account_menu': active_items.filter(location='footer_account'),
        'site_settings': site_settings,
    }
