from django.contrib import admin
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

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
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
            'description': 'Set the discount percentage for all products in this campaign'
        }),
        ('Products', {
            'fields': ('products',)
        }),
    )