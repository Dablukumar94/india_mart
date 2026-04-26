from django.contrib import admin
from .models import Product, ProductImage, Order, OrderItem, Address


# 🔹 Product Image Inline
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# 🔹 Product Admin
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]


# 🔹 Order Item Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# 🔹 Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username')
    inlines = [OrderItemInline]


# 🔹 Address Admin (NEW)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'mobile', 'district', 'state', 'pincode', 'is_default')
    search_fields = ('full_name', 'mobile', 'user__username')
    list_filter = ('is_default', 'state')


# 🔹 Register Models
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Address, AddressAdmin)