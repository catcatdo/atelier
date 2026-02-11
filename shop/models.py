from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'pk']

    def __str__(self):
        return f'{self.product.name} - image {self.pk}'


class ContentImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='content_images')
    image = models.ImageField(upload_to='products/content/')
    number = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f'{self.product.name} - content img {self.number}'


class HeroBanner(models.Model):
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.TextField(blank=True)
    image = models.ImageField(upload_to='banners/')
    crop_x = models.FloatField(default=0)
    crop_y = models.FloatField(default=0)
    crop_width = models.FloatField(default=0)
    crop_height = models.FloatField(default=0)
    text_overlays = models.TextField(blank=True, default='[]')
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    link_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title or f'Banner {self.pk}'


class Popup(models.Model):
    POPUP_TYPE_CHOICES = [
        ('announcement', 'Text + Image Announcement'),
        ('banner', 'Full Image Banner'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='popups/', blank=True, null=True)
    popup_type = models.CharField(max_length=20, choices=POPUP_TYPE_CHOICES, default='announcement')
    is_active = models.BooleanField(default=True)
    link_url = models.URLField(blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    LOCATION_CHOICES = [
        ('header', '네비게이션'),
        ('footer_account', '푸터 계정'),
    ]

    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    label = models.CharField(max_length=100)
    url = models.CharField(max_length=300)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    open_new_tab = models.BooleanField(default=False)

    class Meta:
        ordering = ['location', 'display_order']

    def __str__(self):
        return f'{self.get_location_display()} — {self.label}'


class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/{self.slug}/'


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=200, default="Atelier des Poupées")
    site_tagline = models.CharField(max_length=300, default="Sewn with devotion, worn with grace.")
    site_description = models.TextField(
        default="Handcrafted doll garments inspired by centuries of textile artistry. "
                "Each piece tells a story woven with care and devotion."
    )
    copyright_text = models.CharField(max_length=200, default="Atelier des Poupées")
    color_parchment = models.CharField(max_length=7, default="#FFF3CD")
    color_charcoal = models.CharField(max_length=7, default="#2D2926")
    color_gold = models.CharField(max_length=7, default="#D4AF37")
    color_velvet = models.CharField(max_length=7, default="#8B0000")
    color_leather = models.CharField(max_length=7, default="#8B4513")
    color_leather_light = models.CharField(max_length=7, default="#A0522D")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Site Setting'

    def __str__(self):
        return 'Site Settings'
