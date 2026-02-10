from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.text import slugify
from django.utils import timezone
from django.db import models as db_models
from PIL import Image as PILImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

from .models import Product, Category, ProductImage, ContentImage, HeroBanner, Popup, MenuItem, SiteSetting
from .forms import ProductPostForm, HeroBannerForm, PopupForm
from blog.models import Post


def home_view(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:4]
    latest_products = Product.objects.filter(is_active=True)[:8]
    latest_posts = Post.objects.all()[:3]
    banners = HeroBanner.objects.filter(is_active=True)
    now = timezone.now()
    popups = Popup.objects.filter(is_active=True).filter(
        db_models.Q(start_date__isnull=True) | db_models.Q(start_date__lte=now)
    ).filter(
        db_models.Q(end_date__isnull=True) | db_models.Q(end_date__gte=now)
    )
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'latest_posts': latest_posts,
        'banners': banners,
        'popups': popups,
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
    # Don't show journal section if content is identical to product description
    if post and post.content.strip() == product.description.strip():
        post = None
    content_images = product.content_images.all()
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'post': post,
        'content_images': content_images,
        'related_products': related_products,
    })


# ── Admin Management Views ──


def _unique_slug(base, model, field='slug', instance=None):
    slug = slugify(base)
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


def _crop_image(image_file, crop_x, crop_y, crop_width, crop_height):
    """Crop an uploaded image using coordinates from Cropper.js."""
    img = PILImage.open(image_file)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    left = int(crop_x)
    top = int(crop_y)
    right = int(crop_x + crop_width)
    bottom = int(crop_y + crop_height)

    left = max(0, left)
    top = max(0, top)
    right = min(img.width, right)
    bottom = min(img.height, bottom)

    if crop_width > 0 and crop_height > 0:
        img = img.crop((left, top, right, bottom))

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=90)
    buffer.seek(0)

    name = image_file.name.rsplit('.', 1)[0] + '.jpg'
    return InMemoryUploadedFile(
        buffer, 'ImageField', name,
        'image/jpeg', sys.getsizeof(buffer), None
    )


@staff_member_required
def manage_dashboard_view(request):
    products = Product.objects.select_related('category').order_by('-created_at')
    categories = Category.objects.all()
    banners = HeroBanner.objects.all()
    popups = Popup.objects.all()
    return render(request, 'shop/manage_dashboard.html', {
        'products': products,
        'categories': categories,
        'banners': banners,
        'popups': popups,
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
                price=0,
                description=form.cleaned_data['content'],
                image=image,
                stock=0,
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

            for f in request.FILES.getlist('gallery'):
                ProductImage.objects.create(product=product, image=f)

            existing_count = 0
            for f in request.FILES.getlist('content_images'):
                existing_count += 1
                ContentImage.objects.create(
                    product=product, image=f, number=existing_count
                )

            messages.success(request, f'"{product.name}" has been published.')
            return redirect('manage_edit', pk=product.pk)
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
            product.description = form.cleaned_data['content']
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

            for f in request.FILES.getlist('gallery'):
                ProductImage.objects.create(product=product, image=f)

            existing_count = product.content_images.count()
            for f in request.FILES.getlist('content_images'):
                existing_count += 1
                ContentImage.objects.create(
                    product=product, image=f, number=existing_count
                )

            messages.success(request, f'"{product.name}" has been updated.')
            return redirect('manage_edit', pk=product.pk)
    else:
        form = ProductPostForm(initial={
            'title': product.name,
            'category': product.category,
            'content': product.description,
            'is_featured': product.is_featured,
        })
    return render(request, 'shop/product_form.html', {
        'form': form,
        'editing': True,
        'product': product,
    })


@staff_member_required
def manage_image_delete_view(request, pk):
    img = get_object_or_404(ProductImage, pk=pk)
    product_pk = img.product.pk
    img.image.delete()
    img.delete()
    messages.success(request, 'Image deleted.')
    return redirect('manage_edit', pk=product_pk)


@staff_member_required
def manage_content_image_delete_view(request, pk):
    img = get_object_or_404(ContentImage, pk=pk)
    product_pk = img.product.pk
    img.image.delete()
    img.delete()
    # Renumber remaining content images
    for i, ci in enumerate(ContentImage.objects.filter(product_id=product_pk), 1):
        if ci.number != i:
            ci.number = i
            ci.save()
    messages.success(request, 'Content image deleted. Numbers updated.')
    return redirect('manage_edit', pk=product_pk)


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


# ── Hero Banner Views ──


@staff_member_required
def manage_banner_create_view(request):
    if request.method == 'POST':
        form = HeroBannerForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            crop_x = form.cleaned_data['crop_x']
            crop_y = form.cleaned_data['crop_y']
            crop_w = form.cleaned_data['crop_width']
            crop_h = form.cleaned_data['crop_height']

            if crop_w > 0 and crop_h > 0:
                cropped = _crop_image(image, crop_x, crop_y, crop_w, crop_h)
            else:
                cropped = image

            text_overlays = request.POST.get('text_overlays', '[]')

            HeroBanner.objects.create(
                title=form.cleaned_data.get('title', ''),
                subtitle=form.cleaned_data.get('subtitle', ''),
                image=cropped,
                crop_x=crop_x, crop_y=crop_y,
                crop_width=crop_w, crop_height=crop_h,
                text_overlays=text_overlays,
                is_active=form.cleaned_data['is_active'],
                display_order=form.cleaned_data['display_order'],
                link_url=form.cleaned_data.get('link_url', ''),
            )
            messages.success(request, 'Hero banner created.')
            return redirect('manage_dashboard')
    else:
        form = HeroBannerForm()
    return render(request, 'shop/banner_form.html', {'form': form, 'editing': False})


@staff_member_required
def manage_banner_edit_view(request, pk):
    banner = get_object_or_404(HeroBanner, pk=pk)
    if request.method == 'POST':
        form = HeroBannerForm(request.POST, request.FILES)
        form.fields['image'].required = False
        if form.is_valid():
            banner.title = form.cleaned_data.get('title', '')
            banner.subtitle = form.cleaned_data.get('subtitle', '')
            banner.is_active = form.cleaned_data['is_active']
            banner.display_order = form.cleaned_data['display_order']
            banner.link_url = form.cleaned_data.get('link_url', '')
            banner.text_overlays = request.POST.get('text_overlays', '[]')

            image = form.cleaned_data.get('image')
            if image:
                crop_x = form.cleaned_data['crop_x']
                crop_y = form.cleaned_data['crop_y']
                crop_w = form.cleaned_data['crop_width']
                crop_h = form.cleaned_data['crop_height']
                if crop_w > 0 and crop_h > 0:
                    cropped = _crop_image(image, crop_x, crop_y, crop_w, crop_h)
                else:
                    cropped = image
                banner.image = cropped
                banner.crop_x = crop_x
                banner.crop_y = crop_y
                banner.crop_width = crop_w
                banner.crop_height = crop_h

            banner.save()
            messages.success(request, 'Banner updated.')
            return redirect('manage_dashboard')
    else:
        form = HeroBannerForm(initial={
            'title': banner.title,
            'subtitle': banner.subtitle,
            'is_active': banner.is_active,
            'display_order': banner.display_order,
            'link_url': banner.link_url,
            'crop_x': banner.crop_x,
            'crop_y': banner.crop_y,
            'crop_width': banner.crop_width,
            'crop_height': banner.crop_height,
        })
    return render(request, 'shop/banner_form.html', {
        'form': form, 'editing': True, 'banner': banner,
    })


@staff_member_required
def manage_banner_delete_view(request, pk):
    banner = get_object_or_404(HeroBanner, pk=pk)
    if request.method == 'POST':
        banner.image.delete()
        banner.delete()
        messages.success(request, 'Banner deleted.')
    return redirect('manage_dashboard')


# ── Popup Views ──


@staff_member_required
def manage_popup_create_view(request):
    if request.method == 'POST':
        form = PopupForm(request.POST, request.FILES)
        if form.is_valid():
            Popup.objects.create(
                title=form.cleaned_data['title'],
                popup_type=form.cleaned_data['popup_type'],
                content=form.cleaned_data.get('content', ''),
                image=form.cleaned_data.get('image') or None,
                link_url=form.cleaned_data.get('link_url', ''),
                is_active=form.cleaned_data['is_active'],
                start_date=form.cleaned_data.get('start_date'),
                end_date=form.cleaned_data.get('end_date'),
            )
            messages.success(request, 'Popup created.')
            return redirect('manage_dashboard')
    else:
        form = PopupForm()
    return render(request, 'shop/popup_form.html', {'form': form, 'editing': False})


@staff_member_required
def manage_popup_edit_view(request, pk):
    popup = get_object_or_404(Popup, pk=pk)
    if request.method == 'POST':
        form = PopupForm(request.POST, request.FILES)
        form.fields['image'].required = False
        if form.is_valid():
            popup.title = form.cleaned_data['title']
            popup.popup_type = form.cleaned_data['popup_type']
            popup.content = form.cleaned_data.get('content', '')
            popup.link_url = form.cleaned_data.get('link_url', '')
            popup.is_active = form.cleaned_data['is_active']
            popup.start_date = form.cleaned_data.get('start_date')
            popup.end_date = form.cleaned_data.get('end_date')
            image = form.cleaned_data.get('image')
            if image:
                popup.image = image
            popup.save()
            messages.success(request, 'Popup updated.')
            return redirect('manage_dashboard')
    else:
        form = PopupForm(initial={
            'title': popup.title,
            'popup_type': popup.popup_type,
            'content': popup.content,
            'link_url': popup.link_url,
            'is_active': popup.is_active,
            'start_date': popup.start_date.strftime('%Y-%m-%dT%H:%M') if popup.start_date else '',
            'end_date': popup.end_date.strftime('%Y-%m-%dT%H:%M') if popup.end_date else '',
        })
    return render(request, 'shop/popup_form.html', {
        'form': form, 'editing': True, 'popup': popup,
    })


@staff_member_required
def manage_popup_delete_view(request, pk):
    popup = get_object_or_404(Popup, pk=pk)
    if request.method == 'POST':
        if popup.image:
            popup.image.delete()
        popup.delete()
        messages.success(request, 'Popup deleted.')
    return redirect('manage_dashboard')


# ── Menu Item Views ──


@staff_member_required
def manage_menu_view(request):
    menu_sections = [
        ('header', '네비게이션', MenuItem.objects.filter(location='header')),
        ('footer_account', '푸터 계정', MenuItem.objects.filter(location='footer_account')),
    ]
    locations = MenuItem.LOCATION_CHOICES
    site_settings = SiteSetting.objects.first()
    return render(request, 'shop/manage_menu.html', {
        'menu_sections': menu_sections,
        'locations': locations,
        'site_settings': site_settings,
    })


@staff_member_required
def manage_site_settings_view(request):
    if request.method == 'POST':
        settings, _ = SiteSetting.objects.get_or_create(pk=1)
        settings.site_name = request.POST.get('site_name', '').strip() or settings.site_name
        settings.site_tagline = request.POST.get('site_tagline', '').strip() or settings.site_tagline
        settings.site_description = request.POST.get('site_description', '').strip() or settings.site_description
        settings.copyright_text = request.POST.get('copyright_text', '').strip() or settings.copyright_text
        settings.color_parchment = request.POST.get('color_parchment', '').strip() or settings.color_parchment
        settings.color_charcoal = request.POST.get('color_charcoal', '').strip() or settings.color_charcoal
        settings.color_gold = request.POST.get('color_gold', '').strip() or settings.color_gold
        settings.color_velvet = request.POST.get('color_velvet', '').strip() or settings.color_velvet
        settings.color_leather = request.POST.get('color_leather', '').strip() or settings.color_leather
        settings.color_leather_light = request.POST.get('color_leather_light', '').strip() or settings.color_leather_light
        settings.save()
        messages.success(request, 'Site settings updated.')
    return redirect('manage_menu')


@staff_member_required
def manage_menu_add_view(request):
    if request.method == 'POST':
        location = request.POST.get('location', '').strip()
        label = request.POST.get('label', '').strip()
        url = request.POST.get('url', '').strip()
        display_order = request.POST.get('display_order', '0')
        is_active = request.POST.get('is_active') == 'on'
        open_new_tab = request.POST.get('open_new_tab') == 'on'

        valid_locations = [c[0] for c in MenuItem.LOCATION_CHOICES]
        if label and url and location in valid_locations:
            try:
                display_order = int(display_order)
            except (ValueError, TypeError):
                display_order = 0
            MenuItem.objects.create(
                location=location,
                label=label,
                url=url,
                display_order=display_order,
                is_active=is_active,
                open_new_tab=open_new_tab,
            )
            messages.success(request, f'Menu item "{label}" added.')
        else:
            messages.error(request, 'Label, URL, and valid location are required.')
    return redirect('manage_menu')


@staff_member_required
def manage_menu_edit_view(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        label = request.POST.get('label', '').strip()
        url = request.POST.get('url', '').strip()
        location = request.POST.get('location', '').strip()
        display_order = request.POST.get('display_order', '0')
        is_active = request.POST.get('is_active') == 'on'
        open_new_tab = request.POST.get('open_new_tab') == 'on'

        valid_locations = [c[0] for c in MenuItem.LOCATION_CHOICES]
        if label and url and location in valid_locations:
            try:
                display_order = int(display_order)
            except (ValueError, TypeError):
                display_order = 0
            item.label = label
            item.url = url
            item.location = location
            item.display_order = display_order
            item.is_active = is_active
            item.open_new_tab = open_new_tab
            item.save()
            messages.success(request, f'Menu item "{label}" updated.')
            return redirect('manage_menu')
        else:
            messages.error(request, 'Label, URL, and valid location are required.')

    locations = MenuItem.LOCATION_CHOICES
    return render(request, 'shop/manage_menu_edit.html', {
        'item': item,
        'locations': locations,
    })


@staff_member_required
def manage_menu_delete_view(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        label = item.label
        item.delete()
        messages.success(request, f'Menu item "{label}" deleted.')
    return redirect('manage_menu')
