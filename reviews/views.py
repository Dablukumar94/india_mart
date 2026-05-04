import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from products.models import Product
from reviews.models import Review


class AddReviewAjaxView(LoginRequiredMixin, View):

    def post(self, request):
        data = json.loads(request.body)

        product_id = data.get("product_id")
        rating = int(data.get("rating"))

        product = Product.objects.get(id=product_id)

        review, created = Review.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={"rating": rating}
        )

        return JsonResponse({"success": True})