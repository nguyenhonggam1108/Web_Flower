from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from product.models import Product
from orders.models import Order
from inventory.models import Inventory
from inventory.models import FlowerItem
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class DashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/accounts/login/'  # ✅ nếu chưa đăng nhập, tự chuyển đến login
    redirect_field_name = 'next'

    def test_func(self):
        # ✅ chỉ cho phép admin hoặc staff truy cập dashboard
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        # ✅ nếu khách hàng (không phải staff) → về trang chủ
        if self.request.user.is_authenticated:
            return redirect('index')
        return super().handle_no_permission()

    def get(self, request):
        flowers = FlowerItem.objects.all()
        low_stock_items = []
        low_stock_count = 0
        total_stock = 0

        for f in flowers:
            total_import = Inventory.objects.filter(flower=f, type='IMPORT').aggregate(Sum('quantity'))['quantity__sum'] or 0
            total_export = Inventory.objects.filter(flower=f, type='EXPORT').aggregate(Sum('quantity'))['quantity__sum'] or 0
            stock = total_import - total_export

            total_stock += stock
            if stock < 5:
                low_stock_count += 1
                low_stock_items.append({'flower': f, 'stock': stock})

        # ✅ Lấy dữ liệu nhập/xuất theo ngày để vẽ biểu đồ
        imports = (
            Inventory.objects.filter(type='IMPORT')
            .annotate(date_only=TruncDate('date'))
            .values('date_only')
            .annotate(total=Sum('quantity'))
            .order_by('date_only')
        )

        exports = (
            Inventory.objects.filter(type='EXPORT')
            .annotate(date_only=TruncDate('date'))
            .values('date_only')
            .annotate(total=Sum('quantity'))
            .order_by('date_only')
        )

        labels = [str(i['date_only']) for i in imports]
        import_data = [i['total'] for i in imports]
        export_data = [next((e['total'] for e in exports if e['date_only'] == i['date_only']), 0) for i in imports]

        context = {
            'total_flowers': flowers.count(),
            'total_stock': total_stock,
            'low_stock_count': low_stock_count,
            'low_stock_items': low_stock_items,
            'labels': labels,
            'import_data': import_data,
            'export_data': export_data,
        }

        return render(request, 'dashboard/dashboard.html', context)