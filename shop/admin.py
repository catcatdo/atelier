from django.contrib import admin
from .models import Category, Product, HeroBanner, Popup


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'is_featured', 'created_at')
    list_filter = ('is_active', 'is_featured', 'category')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'is_featured', 'price', 'stock')


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'display_order', 'created_at')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'display_order')


@admin.register(Popup)
class PopupAdmin(admin.ModelAdmin):
    list_display = ('title', 'popup_type', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active', 'popup_type')
    list_editable = ('is_active',)
