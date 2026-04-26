from django.contrib import admin

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'mobile', 'district', 'state', 'pincode', 'is_default')
    search_fields = ('full_name', 'mobile', 'user__username')
    list_filter = ('is_default', 'state')
