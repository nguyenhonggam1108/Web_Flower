from django.utils.http import urlencode
from django.views.generic import FormView, DetailView
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.urls import reverse
from .models import Order, OrderItem, Coupon
from .forms import CheckoutForm
from cart.models import CartItem
from cart.cart_session import Cart
from django.utils import timezone
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from decimal import Decimal
from django.db import models
from django.views import View
from django.core.mail import send_mail
import qrcode
import base64
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items, total = self.get_cart_items()
        context['cart_items'] = cart_items
        context['cart_total'] = total

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

    def post(self, request, *args, **kwargs):
        """Bỏ qua validate để xử lý form tùy chỉnh"""
        return self.form_valid(None)

    def form_valid(self, form):
        cart_items, total = self.get_cart_items()
        if not cart_items:
            messages.error(self.request, "Giỏ hàng trống!")
            return redirect('cart:view_cart')

        # tạo order
        order = Order()

        # Thông tin cơ bản (từ POST)
        order.full_name = self.request.POST.get('full_name', '')
        order.phone = self.request.POST.get('phone', '')
        order.email = self.request.POST.get('email', '')
        order.address = self.request.POST.get('customer_address', '') or ''
        order.note = self.request.POST.get('note', '') or ''

        # shipping_address: nếu khách nhập riêng, dùng nó; nếu không thì dùng address
        shipping_address = self.request.POST.get('shipping_address')
        if shipping_address:
            order.shipping_address = shipping_address
        else:
            order.shipping_address = order.address

        # Xử lý hình thức giao: map POST value sang model constant
        # POST có thể gửi 'pickup' hoặc 'delivery' từ frontend
        order_type = self.request.POST.get('order_type', 'delivery')
        if order_type == 'pickup':
            order.shipping_method = Order.SHIPPING_PICKUP
            # Set a readable address/note for pickup if you want
            order.address = "Khách nhận hàng trực tiếp tại cửa hàng Bloom & Story"
            order.note = (order.note or "") + " | Hình thức: Nhận hàng tại cửa hàng"
        else:
            # default -> giao tận nơi
            order.shipping_method = Order.SHIPPING_DELIVERY
            # ensure shipping_address preserved

        # Gán thông tin user nếu có
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
            if not order.shipping_address and hasattr(self.request.user, 'customer') and order_type != 'pickup':
                order.shipping_address = self.request.user.customer.address

        # Tổng tiền
        order.total_amount = total
        order.final_total = total

        # Xử lý phương thức thanh toán: map POST values -> model constants
        pm = (self.request.POST.get('payment_method', 'cod') or 'cod').lower()
        if pm == 'paypal':
            order.payment_method = Order.PAYMENT_PAYPAL
        elif pm == 'cod':
            order.payment_method = Order.PAYMENT_COD
        elif pm == 'qr':
            # map QR to PAYPAL (online) for display; adjust if you want distinct constant
            order.payment_method = Order.PAYMENT_PAYPAL
        else:
            # fallback
            order.payment_method = Order.PAYMENT_COD

        # Lưu order (lưu trước để có id)
        order.save()
        order.generate_qr()
        order.save()

        # Lưu chi tiết sản phẩm
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )

        # xử lý thanh toán theo phương thức
        if pm == 'paypal':
            # lưu order id vào session và redirect tới payment view
            self.request.session['order_id'] = order.id
            self.request.session['cart_total_vnd'] = float(order.final_total)
            return redirect('orders:payment')

        elif pm == 'qr':
            return redirect(reverse('orders:payment_qr', kwargs={'order_id': order.id}))

        elif pm == 'cod':
            # gửi email xác nhận (COD) trước khi xóa giỏ hàng
            try:
                recipient = order.email or (order.user.email if getattr(order, 'user', None) else None)
                if recipient:
                    subject = f"[Bloom & Story] Xác nhận đơn hàng #{order.id}"
                    text_message = (
                        f"Xin chào {order.full_name},\n\n"
                        f"Chúng tôi đã nhận đơn hàng #{order.id}. Tổng: {order.final_total} VND.\n"
                        "Bạn sẽ thanh toán khi nhận hàng (COD).\n\n"
                        "Cảm ơn bạn đã mua hàng tại Bloom & Story."
                    )
                    html_message = f"""
                        <p>Xin chào <strong>{order.full_name}</strong>,</p>
                        <p>Chúng tôi đã nhận đơn hàng <strong>#{order.id}</strong>.</p>
                        <p><strong>Tổng cộng:</strong> {order.final_total} VND</p>
                        <p>Hình thức thanh toán: <strong>COD</strong> (thu khi nhận hàng)</p>
                        <p>Chúng tôi sẽ liên hệ để xác nhận và giao hàng sớm nhất 💐</p>
                    """
                    send_mail(
                        subject,
                        text_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [recipient],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    logger.info("Sent order confirmation (COD) to %s for order %s", recipient, order.id)
                else:
                    logger.warning("No recipient found for order %s (COD) — skipping email", order.id)
            except Exception as e:
                logger.exception("Error sending COD confirmation email for order %s: %s", order.id, e)
                # don't block flow; warn user
                messages.warning(self.request, "Không gửi được email xác nhận — kiểm tra cấu hình email.")

            # xóa giỏ hàng
            if self.request.user.is_authenticated:
                CartItem.objects.filter(user=self.request.user).delete()
            else:
                Cart(self.request).clear()

            messages.success(self.request, "Đặt hàng thành công! Thanh toán khi nhận hàng.")
            return redirect(reverse('orders:order_success', kwargs={'order_id': order.id}))

        # default
        messages.success(self.request, "Đặt hàng thành công!")
        return redirect(reverse('orders:order_success', kwargs={'order_id': order.id}))


class OrderSuccessView(DetailView):
    model = Order
    template_name = 'orders/orders_success.html'
    context_object_name = 'order'

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        return get_object_or_404(Order, id=order_id)


class PaymentView(FormView):
    """Hiển thị form thanh toán PayPal"""
    template_name = 'orders/payment.html'

    def get(self, request, *args, **kwargs):
        order_id = request.session.get('order_id')
        total_vnd = request.session.get('cart_total_vnd')

        if not order_id or not total_vnd:
            messages.error(request, "Không tìm thấy đơn hàng cần thanh toán.")
            return redirect('orders:checkout')

        # Quy đổi từ VND → USD (1 USD = 24,000 VND)
        rate = Decimal('24000')
        usd_amount = (Decimal(total_vnd) / rate).quantize(Decimal('0.01'))

        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': str(usd_amount),
            'item_name': f'Đơn hàng #{order_id} - Bloom & Story',
            'invoice': f'INV-{order_id}',
            'currency_code': 'USD',
            'notify_url': request.build_absolute_uri('/paypal/'),
            'return_url': request.build_absolute_uri(reverse('orders:payment_done')),
            'cancel_return': request.build_absolute_uri(reverse('orders:payment_cancelled')),
        }

        form = PayPalPaymentsForm(initial=paypal_dict)
        context = {
            'form': form,
            'usd_amount': usd_amount,
            'total_vnd': total_vnd
        }
        return render(request, self.template_name, context)


class PaymentQRView(View):
    template_name = 'orders/payment_qr.html'

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if order.is_paid:
            return redirect(reverse('orders:order_success', kwargs={'order_id': order.id}))

        # Chuyển VND -> USD
        rate = getattr(settings, 'VND_TO_USD_RATE', 24000)
        usd_amount = (Decimal(order.final_total) / Decimal(rate)).quantize(Decimal('0.01'))

        # Sử dụng sandbox
        use_sandbox = getattr(settings, 'PAYPAL_USE_SANDBOX', True)
        if use_sandbox:
            base_url = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
            business_email = getattr(settings, 'PAYPAL_RECEIVER_EMAIL')
        else:
            base_url = 'https://www.paypal.com/cgi-bin/webscr'
            business_email = getattr(settings, 'PAYPAL_RECEIVER_EMAIL')

        # Tạo link thanh toán classic cgi-bin/webscr
        params = {
            'cmd': '_xclick',
            'business': business_email,
            'amount': str(usd_amount),
            'currency_code': 'USD',
            'item_name': f'Đơn hàng #{order.id} - Bloom & Story',
            'invoice': f'INV-{order.id}',
            'return': request.build_absolute_uri(reverse('orders:payment_done')),
            'cancel_return': request.build_absolute_uri(reverse('orders:payment_cancelled')),
        }
        payment_link = base_url + '?' + urlencode(params)

        # Tạo QR code
        qr_img = qrcode.make(payment_link)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        context = {
            'order': order,
            'qr_base64': qr_base64,
            'paypal_link': payment_link,
            'usd_amount': usd_amount,
            'vnd_amount': order.final_total,
        }
        return render(request, self.template_name, context)

    def post(self, request, order_id):
        # Xác nhận thanh toán thủ công
        order = get_object_or_404(Order, id=order_id)
        order.is_paid = True
        order.status = 'paid'
        order.save()

        # Xóa giỏ hàng
        if request.user.is_authenticated:
            CartItem.objects.filter(user=request.user).delete()
        else:
            Cart(request).clear()

        return redirect(reverse('orders:order_success', kwargs={'order_id': order.id}))


class PaymentDoneView(FormView):
    """Xử lý sau khi thanh toán thành công"""
    template_name = 'orders/payment_done.html'

    def get(self, request, *args, **kwargs):
        order_id = request.session.get('order_id')
        if not order_id:
            messages.error(request, "Không tìm thấy thông tin đơn hàng.")
            return redirect('orders:checkout')

        order = Order.objects.filter(id=order_id).first()
        if order:
            order.is_paid = True
            order.status = 'paid'
            order.save()

            # Gửi email xác nhận thanh toán
            try:
                recipient = order.email or (order.user.email if getattr(order, 'user', None) else None)
                if recipient:
                    subject = f"[Bloom & Story] Xác nhận thanh toán đơn hàng #{order.id}"
                    text_message = (
                        f"Xin chào {order.full_name},\n\n"
                        f"Bloom & Story xác nhận bạn đã thanh toán đơn hàng #{order.id}.\n"
                        f"Tổng: {order.final_total} VND.\n\n"
                        "Cảm ơn bạn đã mua hàng tại Bloom & Story."
                    )
                    html_message = f"""
                        <p>Xin chào <strong>{order.full_name}</strong>,</p>
                        <p>Bloom & Story xác nhận bạn đã thanh toán đơn hàng <strong>#{order.id}</strong>.</p>
                        <p><strong>Tổng cộng:</strong> {order.final_total} VND</p>
                        <p>Chúng tôi sẽ xử lý và giao hàng sớm nhất 💐</p>
                    """
                    send_mail(
                        subject,
                        text_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [recipient],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    logger.info("Sent payment confirmation to %s for order %s", recipient, order.id)
                else:
                    logger.warning("No recipient found for order %s (payment done) — skipping email", order.id)
            except Exception as e:
                logger.exception("Error sending payment confirmation email for order %s: %s", order.id, e)
                messages.warning(request, "Không gửi được email xác nhận (vui lòng kiểm tra cấu hình email).")

            # Xóa giỏ hàng sau khi thanh toán thành công
            if request.user.is_authenticated:
                CartItem.objects.filter(user=request.user).delete()
            else:
                Cart(request).clear()

        # Xóa session sau khi thanh toán xong
        request.session.pop('order_id', None)
        request.session.pop('cart_total_vnd', None)

        messages.success(request, "Thanh toán PayPal thành công!")
        return redirect(reverse('orders:order_success', kwargs={'order_id': order.id}))


class PaymentCancelledView(FormView):
    """Khi người dùng hủy thanh toán"""
    template_name = 'orders/payment_cancelled.html'

    def get(self, request, *args, **kwargs):
        messages.warning(request, "Bạn đã hủy thanh toán PayPal.")
        return redirect('orders:checkout')