import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect

from products.models import Product
from reviews.models import Review
from orders.models import OrderItem


class AddReviewView(LoginRequiredMixin, View):
    login_url = 'login'


    # =========================
    # GET → Review Page
    # =========================
    def get(self, request):
        product_id = request.GET.get("product")

        if not product_id:
            return redirect("products")

        product = get_object_or_404(Product, id=product_id)

        # 🔥 find last delivered order (for redirect safety)
        order_item = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status="DELIVERED"
        ).select_related("order").first()

        order = order_item.order if order_item else None

        return render(request, "reviews/add_review.html", {
            "product": product,
            "order": order
        })


    # =========================
    # POST → AJAX Review Save
    # =========================
    def post(self, request):

        try:
            data = json.loads(request.body)

            product_id = data.get("product_id")
            rating = data.get("rating")
            comment = data.get("comment")

            # 🔥 validate product
            product = get_object_or_404(Product, id=product_id)

            # 🔥 rating validation
            if rating is None or rating == "":
                return JsonResponse({
                    "success": False,
                    "message": "Rating is required"
                }, status=400)

            try:
                rating = int(rating)
            except:
                return JsonResponse({
                    "success": False,
                    "message": "Invalid rating"
                }, status=400)

            if rating < 1 or rating > 5:
                return JsonResponse({
                    "success": False,
                    "message": "Rating must be between 1 and 5"
                }, status=400)

            # 🔥 clean comment
            comment = comment.strip() if comment else None

            # 🔥 buyer check
            has_purchased = OrderItem.objects.filter(
                order__user=request.user,
                product=product,
                order__status="DELIVERED"
            ).exists()

            if not has_purchased:
                return JsonResponse({
                    "success": False,
                    "message": "Only verified buyers can review"
                }, status=403)

            # ⭐ save / update review
            review, created = Review.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={
                    "rating": rating,
                    "comment": comment
                }
            )

            return JsonResponse({
                "success": True,
                "created": created,
                "rating": review.rating,
                "comment": review.comment
            })

        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": str(e)
            }, status=500)