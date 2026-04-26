from django.views import View
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Product


# --------------------
# PRODUCT LIST
# --------------------
class ProductListView(View):
    def get(self, request):
        product_list = Product.objects.all()

        paginator = Paginator(product_list, 8)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

        return render(request, "products/plp.html", {"products": products})


# --------------------
# PRODUCT DETAIL
# --------------------
class ProductDetailView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        return render(request, "products/pdp.html", {"product": product})
