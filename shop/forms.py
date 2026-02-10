from django import forms
from .models import Product, Category


class ProductPostForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Enter title...'}),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label='Select a category',
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
    )
    stock = forms.IntegerField(
        min_value=0,
        initial=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Stock quantity'}),
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,
            'placeholder': 'Write your description and story...',
        }),
    )
    image = forms.ImageField(required=False)
    is_featured = forms.BooleanField(required=False, label='Feature on homepage')


class HeroBannerForm(forms.Form):
    title = forms.CharField(max_length=200, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Banner title (optional)'}))
    subtitle = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Subtitle text (optional)'}))
    image = forms.ImageField(required=True)
    link_url = forms.URLField(required=False,
        widget=forms.URLInput(attrs={'placeholder': 'https://...'}))
    is_active = forms.BooleanField(required=False, initial=True)
    display_order = forms.IntegerField(min_value=0, initial=0,
        widget=forms.NumberInput(attrs={'placeholder': '0'}))
    crop_x = forms.FloatField(widget=forms.HiddenInput(), initial=0)
    crop_y = forms.FloatField(widget=forms.HiddenInput(), initial=0)
    crop_width = forms.FloatField(widget=forms.HiddenInput(), initial=0)
    crop_height = forms.FloatField(widget=forms.HiddenInput(), initial=0)


class PopupForm(forms.Form):
    POPUP_TYPE_CHOICES = [
        ('announcement', 'Text + Image Announcement'),
        ('banner', 'Full Image Banner'),
    ]

    title = forms.CharField(max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Popup title...'}))
    popup_type = forms.ChoiceField(choices=POPUP_TYPE_CHOICES)
    content = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Announcement text...'}))
    image = forms.ImageField(required=False)
    link_url = forms.URLField(required=False,
        widget=forms.URLInput(attrs={'placeholder': 'https://... (optional link)'}))
    is_active = forms.BooleanField(required=False, initial=True)
    start_date = forms.DateTimeField(required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_date = forms.DateTimeField(required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
