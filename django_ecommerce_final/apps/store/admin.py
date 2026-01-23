from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from .models import Product, Category, Campaign

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'stock', 'is_featured')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class CampaignAdminForm(forms.ModelForm):
    """Custom form for Campaign admin to validate discount_percent"""
    class Meta:
        model = Campaign
        fields = '__all__'
    
    def clean_discount_percent(self):
        discount_percent = self.cleaned_data.get('discount_percent')
        if discount_percent is not None:
            if discount_percent < 0:
                raise ValidationError('Discount percentage cannot be negative. Only positive values (0-100) are allowed.')
            if discount_percent > 100:
                raise ValidationError('Discount percentage cannot exceed 100%.')
        return discount_percent

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    form = CampaignAdminForm
    list_display = ('title', 'start_time', 'end_time', 'discount_percent', 'is_active')
    filter_horizontal = ('products',)
    fieldsets = (
        ('Campaign Info', {
            'fields': ('title', 'image', 'is_active')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Discount', {
            'fields': ('discount_percent',),
            'description': 'Set the discount percentage for all products in this campaign (0-100). Only positive values are allowed.'
        }),
        ('Products', {
            'fields': ('products',)
        }),
    )