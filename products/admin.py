from django.contrib import admin
from .models import Product, ProductImage, Order, OrderItem


# 🔹 Product Image Inline
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# 🔹 Product Admin
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]


# 🔹 Order Item Inline (VERY USEFUL)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# 🔹 Order Admin (Professional)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'id')
    inlines = [OrderItemInline]


# 🔹 Register Models
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)