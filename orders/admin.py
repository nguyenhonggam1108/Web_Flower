# Register your models here.
from django.contrib import admin
from .models import Order, OrderItem, DeliveryProof, ShippingArea, Coupon

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'total_amount', 'shipping_method_display', 'payment_method_display', 'status', 'created_at')
    list_filter = ('status', 'shipping_method', 'payment_method', 'created_at')
    search_fields = ('full_name', 'phone', 'email')
    readonly_fields = ('qr_code_preview', 'total_amount', 'final_total', 'created_at')
    inlines = [OrderItemInline]

    def shipping_method_display(self, obj):
        return obj.get_shipping_method_display()
    shipping_method_display.short_description = 'Giao hàng'

    def payment_method_display(self, obj):
        return obj.get_payment_method_display()
    payment_method_display.short_description = 'Thanh toán'

    fieldsets = (
        ('Thông tin khách hàng', {
            'fields': ('full_name', 'phone', 'email', 'address', 'shipping_address', 'note')
        }),
        ('Thông tin đơn hàng', {
            'fields': ('total_amount', 'final_total', 'status', 'qr_code_preview', 'created_at', 'shipping_method', 'payment_method')
        }),
    )

    def qr_code_preview(self, obj):
        """Hiển thị ảnh QR trực tiếp trong admin"""
        if obj.qr_code:
            return f'<img src="{obj.qr_code.url}" width="120" height="120" />'
        return "(Chưa có mã QR)"
    qr_code_preview.allow_tags = True
    qr_code_preview.short_description = "Mã QR"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')

admin.site.register(DeliveryProof)
admin.site.register(ShippingArea)
admin.site.register(Coupon)