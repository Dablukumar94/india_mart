from django.views import View
from django.shortcuts import render
from orders.models import Order
from django.db.models import Sum, Count
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.mixins import UserPassesTestMixin


class AdminDashboardView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):

        days = int(request.GET.get('range', 7))

        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0

        pending_orders = Order.objects.filter(status='PLACED').count()
        delivered_orders = Order.objects.filter(status='DELIVERED').count()

        labels = []
        order_data = []
        revenue_data = []

        for i in range(days - 1, -1, -1):
            day = now().date() - timedelta(days=i)

            daily_orders = Order.objects.filter(created_at__date=day)
            count = daily_orders.count()
            revenue = daily_orders.aggregate(total=Sum('total_amount'))['total'] or 0

            labels.append(day.strftime("%d %b"))
            order_data.append(count)
            revenue_data.append(float(revenue))

        # 🍕 Pie chart
        status_data = Order.objects.values('status').annotate(count=Count('id'))

        pie_labels = [item['status'] for item in status_data]
        pie_counts = [item['count'] for item in status_data]

        context = {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,

            # ❌ NO json.dumps
            'labels': labels,
            'order_data': order_data,
            'revenue_data': revenue_data,
            'pie_labels': pie_labels,
            'pie_counts': pie_counts,

            'selected_range': days
        }

        return render(request, 'dashboard/dashboard.html', context)