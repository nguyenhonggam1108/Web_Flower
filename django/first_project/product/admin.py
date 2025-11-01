from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html

from .models import Product, ProductImage


# Tùy chỉnh hiển thị trong admin (không bắt buộc)
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # số dòng trống để thêm ảnh mới


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_category', 'price', 'status')
    search_fields = ('name',)
    list_filter = ('category', 'status', 'is_featured')
    inlines = [ProductImageInline]

    def get_category(self, obj):
        # Trả về tên danh mục (vì 1 sản phẩm chỉ có 1 category)
        return obj.category.name if obj.category else "-"

    get_category.short_description = 'Danh mục'  # tiêu đề cột trong admin


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'show_image')

    # ✅ Thêm hàm hiển thị ảnh thu nhỏ trong admin
    def show_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="80" style="object-fit:cover; border-radius:5px;"/>',
                               obj.image.url)
        return "(No Image)"

    show_image.short_description = "Ảnh"

