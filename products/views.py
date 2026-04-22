# from django.shortcuts import render, redirect
# from django.contrib import messages

# # Create your views here.

# # messages.success(request, "Data saved successfully!")
# # messages.error(request, "Something went wrong!")
# # messages.warning(request, "Please check your form!")
# # messages.info(request, "Welcome back!")

# def index_page(request):
#     messages.success(request, "Data saved successfully!")
#     return render(request, "base/base.html")


from django.views import View
from django.shortcuts import render
from .models import Product
from django.shortcuts import get_object_or_404


class ProductListView(View):

    def get(self, request):
        products = Product.objects.all()
        return render(request, "products/plp.html", {"products": products})
    

class ProductDetailView(View):
    def get(self, request, id):
        product = get_object_or_404(Product, id=id)
        return render(request, "products/pdp.html", {"product": product})