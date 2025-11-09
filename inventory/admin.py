from django.contrib import admin
from .models import FlowerCategory, Supplier, FlowerItem, Inventory, GoodsReceipt, GoodsReceiptItem

@admin.register(FlowerCategory)
class FlowerCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name','phone','email')

@admin.register(FlowerItem)
class FlowerItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'supplier', 'price', 'stock_bunches')
    list_filter = ('category','supplier')
    search_fields = ('name',)
    # nếu muốn tạo/edit category trên cùng form, bạn có thể thêm Inline hoặc custom form

# giữ đăng ký Inventory / GoodsReceipt nếu bạn có
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('flower', 'quantity', 'type', 'staff', 'date')
    list_filter = ('type', 'date')

class GoodsReceiptItemInline(admin.TabularInline):
    model = GoodsReceiptItem
    extra = 0

@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    inlines = [GoodsReceiptItemInline]
    list_display = ('id','supplier','created_at','total_amount')
    readonly_fields = ('total_amount','created_at')