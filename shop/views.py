from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from blog.models import Post


def home_view(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:4]
    latest_products = Product.objects.filter(is_active=True)[:8]
    latest_posts = Post.objects.all()[:3]
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'latest_posts': latest_posts,
    })


def product_list_view(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
    })


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })
