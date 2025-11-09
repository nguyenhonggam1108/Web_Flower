from django.urls import path, include
from .views import CheckoutView, OrderSuccessView, PaymentView, PaymentDoneView, PaymentCancelledView, PaymentQRView

app_name = 'orders'

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-success/<int:order_id>/', OrderSuccessView.as_view(), name='order_success'),
    path('paypal/', include('paypal.standard.ipn.urls')),  # IPN endpoint
    path('payment/', PaymentView.as_view(), name='payment'),
    path('payment-qr/<int:order_id>/', PaymentQRView.as_view(), name='payment_qr'),
    path('payment_done/', PaymentDoneView.as_view(), name='payment_done'),
    path('payment_cancelled/', PaymentCancelledView.as_view(), name='payment_cancelled'),
]
