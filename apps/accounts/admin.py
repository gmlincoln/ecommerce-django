from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'city', 'country')
    list_filter = ('country', 'city')
    search_fields = ('user__username', 'user__email', 'full_name', 'phone')
    ordering = ('user__username',)