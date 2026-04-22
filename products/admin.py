# from django.contrib import admin
# from .models import Product, ProductImage

# admin.site.register(Product)
# admin.site.register(ProductImage)

from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]


admin.site.register(Product, ProductAdmin)