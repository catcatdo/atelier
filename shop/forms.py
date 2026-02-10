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
