from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Product, ProductImage


# Tùy chỉnh hiển thị trong admin (không bắt buộc)
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # số dòng trống để thêm ảnh mới


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_categories', 'price', 'status')
    search_fields = ('name',)
    filter_horizontal = ('category',)
    list_filter = ('is_featured', 'status')
    inlines = [ProductImageInline]

    def get_categories(self, obj):
        # Trả về danh sách tên category, nối bằng dấu phẩy
        return ", ".join([c.name for c in obj.category.all()])

    get_categories.short_description = 'Danh mục'  # tiêu đề cột trong admin

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id','product', 'image_url')
