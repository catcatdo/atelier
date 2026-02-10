from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.text import slugify

from .models import Product, Category
from .forms import ProductPostForm
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
    post = Post.objects.filter(related_product=product).first()
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'post': post,
        'related_products': related_products,
    })


# ── Admin Management Views ──


def _unique_slug(base, model, field='slug', instance=None):
    slug = slugify(base, allow_unicode=True)
    if not slug:
        slug = 'item'
    qs = model.objects.all()
    if instance:
        qs = qs.exclude(pk=instance.pk)
    candidate, n = slug, 1
    while qs.filter(**{field: candidate}).exists():
        candidate = f'{slug}-{n}'
        n += 1
    return candidate


@staff_member_required
def manage_dashboard_view(request):
    products = Product.objects.select_related('category').order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'shop/manage_dashboard.html', {
        'products': products,
        'categories': categories,
    })


@staff_member_required
def manage_category_add_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            slug = _unique_slug(name, Category)
            Category.objects.create(name=name, slug=slug)
            messages.success(request, f'Category "{name}" created.')
        else:
            messages.error(request, 'Category name is required.')
    return redirect('manage_dashboard')


@staff_member_required
def manage_category_delete_view(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if cat.products.exists():
        messages.error(request, f'Cannot delete "{cat.name}" — it still has products.')
    else:
        name = cat.name
        cat.delete()
        messages.success(request, f'Category "{name}" deleted.')
    return redirect('manage_dashboard')


@staff_member_required
def manage_create_view(request):
    if request.method == 'POST':
        form = ProductPostForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get('image') or None

            product = Product.objects.create(
                name=form.cleaned_data['title'],
                slug=_unique_slug(form.cleaned_data['title'], Product),
                category=form.cleaned_data['category'],
                price=form.cleaned_data['price'],
                description=form.cleaned_data['content'],
                image=image,
                stock=form.cleaned_data['stock'],
                is_active=True,
                is_featured=form.cleaned_data['is_featured'],
            )

            if image:
                image.seek(0)

            Post.objects.create(
                title=form.cleaned_data['title'],
                slug=_unique_slug(form.cleaned_data['title'], Post),
                content=form.cleaned_data['content'],
                author=request.user,
                related_product=product,
                image=image,
            )
            messages.success(request, f'"{product.name}" has been published.')
            return redirect('manage_dashboard')
    else:
        form = ProductPostForm()
    return render(request, 'shop/product_form.html', {
        'form': form,
        'editing': False,
    })


@staff_member_required
def manage_edit_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    post = Post.objects.filter(related_product=product).first()

    if request.method == 'POST':
        form = ProductPostForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get('image') or None

            product.name = form.cleaned_data['title']
            product.slug = _unique_slug(form.cleaned_data['title'], Product, instance=product)
            product.category = form.cleaned_data['category']
            product.price = form.cleaned_data['price']
            product.description = form.cleaned_data['content']
            product.stock = form.cleaned_data['stock']
            product.is_featured = form.cleaned_data['is_featured']
            if image:
                product.image = image
            product.save()

            if post:
                post.title = form.cleaned_data['title']
                post.slug = _unique_slug(form.cleaned_data['title'], Post, instance=post)
                post.content = form.cleaned_data['content']
                if image:
                    image.seek(0)
                    post.image = image
                post.save()

            messages.success(request, f'"{product.name}" has been updated.')
            return redirect('manage_dashboard')
    else:
        form = ProductPostForm(initial={
            'title': product.name,
            'category': product.category,
            'price': product.price,
            'stock': product.stock,
            'content': product.description,
            'is_featured': product.is_featured,
        })
    return render(request, 'shop/product_form.html', {
        'form': form,
        'editing': True,
        'product': product,
    })


@staff_member_required
def manage_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        Post.objects.filter(related_product=product).delete()
        name = product.name
        product.delete()
        messages.success(request, f'"{name}" has been deleted.')
        return redirect('manage_dashboard')
    return render(request, 'shop/product_confirm_delete.html', {
        'product': product,
    })
