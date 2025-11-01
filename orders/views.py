from django.views.generic import FormView, DetailView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .models import Order, OrderItem, Coupon
from .forms import CheckoutForm
from cart.models import CartItem
from cart.cart_session import Cart
from django.utils import timezone
from django.db import models

class CheckoutView(FormView):
    template_name = 'orders/checkout.html'
    form_class = CheckoutForm

    def get_cart_items(self):
        """Lấy danh sách sản phẩm trong giỏ hàng"""
        if self.request.user.is_authenticated:
            items = CartItem.objects.filter(user=self.request.user).select_related('product')
            cart_data = []
            for item in items:
                cart_data.append({
                    'product': item.product,
                    'quantity': item.quantity,
                    'price': item.product.price,
                    'total_price': item.product.price * item.quantity,
                })
            total = sum(i['total_price'] for i in cart_data)
            return cart_data, total
        else:
            cart = Cart(self.request)
            cart_data = list(cart)
            total = cart.get_total_price()
            return cart_data, total

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user

        if user.is_authenticated:
            initial.update({
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'email': user.email,
            })
            # ✅ Lấy dữ liệu từ Customer model
            customer = getattr(user, 'customer', None)
            if customer:
                initial.update({
                    'phone': customer.phone or '',
                    'address': customer.address or '',
                })
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items, total = self.get_cart_items()
        context['cart_items'] = cart_items
        context['cart_total'] = total

        # ✅ Thêm danh sách coupon hợp lệ (chỉ khi user đã đăng nhập)
        if self.request.user.is_authenticated:
            available_coupons = Coupon.objects.filter(
                active=True,
            ).filter(
                models.Q(start_date__lte=timezone.now()) | models.Q(start_date__isnull=True),
                models.Q(expiry_date__gte=timezone.now()) | models.Q(expiry_date__isnull=True)
            ).order_by('-start_date')
            context['available_coupons'] = available_coupons
        else:
            context['available_coupons'] = None

        return context

    def form_valid(self, form):
        """Xử lý khi người dùng bấm nút 'Đặt hàng' hoặc 'Nhận hàng tại cửa hàng'"""
        cart_items, total = self.get_cart_items()
        if not cart_items:
            messages.error(self.request, "Giỏ hàng trống!")
            return redirect('cart:view_cart')

        order = form.save(commit=False)

        # ✅ Gán địa chỉ nhận hàng riêng
        shipping_address = self.request.POST.get('shipping_address')
        if shipping_address:
            order.shipping_address = shipping_address
        else:
            order.shipping_address = order.address

        # ✅ Kiểm tra loại đơn hàng
        order_type = self.request.POST.get('order_type', 'delivery')  # mặc định là giao tận nơi
        if order_type == 'pickup':
            order.address = "Khách nhận hàng trực tiếp tại cửa hàng Bloom & Story"
            order.note = (order.note or "") + " | Hình thức: Nhận hàng tại cửa hàng"

        # ✅ Gán thông tin user (nếu đăng nhập)
        if self.request.user.is_authenticated:
            order.user = self.request.user
            if not order.full_name:
                order.full_name = f"{self.request.user.first_name} {self.request.user.last_name}".strip() or self.request.user.username
            if not order.email:
                order.email = self.request.user.email
            if not order.phone and hasattr(self.request.user, 'customer'):
                order.phone = self.request.user.customer.phone
            if not order.address and hasattr(self.request.user, 'customer') and order_type != 'pickup':
                order.address = self.request.user.customer.address

        order.total_amount = total
        order.final_total = total
        order.save()
        order.generate_qr()  # Sinh mã QR
        order.save()

        # ✅ Lưu các sản phẩm
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )

        # ✅ Xóa giỏ hàng
        if self.request.user.is_authenticated:
            CartItem.objects.filter(user=self.request.user).delete()
        else:
            Cart(self.request).clear()

        # ✅ Hoàn tất
        messages.success(self.request, "Đặt hàng thành công!")
        return redirect(reverse('orders:order_success', kwargs={'order_id': order.id}))

class OrderSuccessView(DetailView):
    model = Order
    template_name = 'orders/orders_success.html'
    context_object_name = 'order'

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        return get_object_or_404(Order, id=order_id)
