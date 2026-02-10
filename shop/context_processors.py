from .models import MenuItem, SiteSetting


def menu_context(request):
    active_items = MenuItem.objects.filter(is_active=True)
    site_settings = SiteSetting.objects.first()
    return {
        'header_menu': active_items.filter(location='header'),
        'footer_nav_menu': active_items.filter(location='footer_nav'),
        'footer_account_menu': active_items.filter(location='footer_account'),
        'site_settings': site_settings,
    }
