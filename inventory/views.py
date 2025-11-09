from decimal import Decimal, InvalidOperation
import logging
from django.apps import apps as django_apps
from django.contrib.auth import apps
from django.contrib.contenttypes.models import ContentType
from django.forms import modelform_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import ListView, DetailView

from .forms import GoodsReceiptForm, GoodsReceiptItemFormSet
from .models import (
    Inventory,
    FlowerCategory,
    FlowerItem,
    Supplier,
    GoodsReceipt,
    GoodsReceiptItem,
)

from django.db.models import Sum

logger = logging.getLogger(__name__)


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff


# ---------- Inventory (nhập lẻ / xuất lẻ) ----------
class InventoryListView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        inventory_qs = Inventory.objects.select_related('flower', 'staff').order_by('-date')
        return render(request, 'inventory/inventory_list.html', {'inventory': inventory_qs})


class InventoryCreateView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        flowers = FlowerItem.objects.select_related('supplier', 'category').all()
        suppliers = Supplier.objects.all()

        # flower categories: try FlowerCategory model first, fallback build from flowers
        flower_cats = []
        try:
            FlowerCategoryModel = django_apps.get_model('inventory', 'FlowerCategory')
            flower_cats = list(FlowerCategoryModel.objects.order_by('name').values('id', 'name'))
        except LookupError:
            seen = set()
            for f in flowers:
                if getattr(f, 'category', None) and f.category.id not in seen:
                    flower_cats.append({'id': f.category.id, 'name': f.category.name})
                    seen.add(f.category.id)

        # accessory categories (if accessories app installed)
        accessory_cats = []
        try:
            AccCategory = django_apps.get_model('accessories', 'AccessoryCategory')
            accessory_cats = list(AccCategory.objects.order_by('name').values('id', 'name'))
        except LookupError:
            accessory_cats = []

        item_app_default = request.GET.get('item_app', 'inventory')

        return render(request, 'inventory/inventory_form.html', {
            'flowers': flowers,
            'suppliers': suppliers,
            'flower_cats': flower_cats,
            'accessory_cats': accessory_cats,
            'item_app_default': item_app_default,
        })

    def post(self, request, *args, **kwargs):
        # read generic item selection
        item_app = request.POST.get('item_app')         # 'inventory' or 'accessories'
        item_model = request.POST.get('item_model')     # 'FlowerItem' or 'AccessoryItem'
        item_id = request.POST.get('item_id')           # pk of selected item
        inv_type = request.POST.get('type') or 'IMPORT' # IMPORT or EXPORT

        # quantity validation
        try:
            quantity = int(request.POST.get('quantity', 0))
            if quantity <= 0:
                raise ValueError("Số lượng phải > 0")
        except (TypeError, ValueError):
            messages.error(request, "Số lượng không hợp lệ (phải là số nguyên dương).")
            return redirect('inventory:add')

        # unit price (optional; used to compute total)
        unit_price_raw = request.POST.get('unit_price', '').strip()
        try:
            unit_price = Decimal(unit_price_raw) if unit_price_raw != '' else None
        except (InvalidOperation, ValueError):
            messages.error(request, "Đơn giá không hợp lệ.")
            return redirect('inventory:add')

        if not item_app or not item_model or not item_id:
            messages.error(request, "Bạn chưa chọn vật phẩm để nhập/xuất.")
            return redirect('inventory:add')

        # safe transaction + row locking
        try:
            with transaction.atomic():
                Model = django_apps.get_model(item_app, item_model)
                item = Model.objects.select_for_update().get(pk=item_id)

                # determine stock field and update
                if hasattr(item, 'stock_bunches'):
                    current = int(item.stock_bunches or 0)
                    if inv_type == 'EXPORT':
                        if quantity > current:
                            messages.error(request, f"Không đủ tồn: hiện có {current} đơn vị.")
                            return redirect('inventory:add')
                        item.stock_bunches = current - quantity
                    else:
                        item.stock_bunches = current + quantity
                elif hasattr(item, 'stock'):
                    current = int(item.stock or 0)
                    if inv_type == 'EXPORT':
                        if quantity > current:
                            messages.error(request, f"Không đủ tồn: hiện có {current} đơn vị.")
                            return redirect('inventory:add')
                        item.stock = current - quantity
                    else:
                        item.stock = current + quantity
                else:
                    messages.error(request, "Model được chọn không hỗ trợ quản lý tồn.")
                    return redirect('inventory:add')

                item.save()

                # compute total_value if unit_price provided
                total_value = None
                if unit_price is not None:
                    total_value = (unit_price * Decimal(quantity))

                # prepare Inventory record kwargs
                inventory_kwargs = {
                    'quantity': quantity,
                    'type': inv_type,
                    'note': request.POST.get('note', '') or f"{item_app}.{item_model} id={item_id}",
                    'staff': request.user,
                }
                # if this is a FlowerItem, set flower FK for backward compatibility
                if item_app == 'inventory' and item_model.lower() in ('floweritem',):
                    try:
                        inventory_kwargs['flower'] = Model.objects.get(pk=item_id)
                    except Exception:
                        inventory_kwargs['flower'] = None

                # attach unit_price / total_value if Inventory model has these fields
                try:
                    Inventory._meta.get_field('unit_price')
                    inventory_kwargs['unit_price'] = unit_price
                except Exception:
                    if unit_price is not None:
                        inventory_kwargs['note'] = (inventory_kwargs.get('note') or '') + f" | unit_price={unit_price}"

                try:
                    Inventory._meta.get_field('total_value')
                    inventory_kwargs['total_value'] = total_value
                except Exception:
                    if total_value is not None:
                        inventory_kwargs['note'] = (inventory_kwargs.get('note') or '') + f" | total={total_value}"

                Inventory.objects.create(**inventory_kwargs)

        except Model.DoesNotExist:
            messages.error(request, "Vật phẩm không tồn tại.")
            return redirect('inventory:add')
        except Exception as e:
            messages.error(request, f"Có lỗi khi xử lý: {e}")
            return redirect('inventory:add')

        messages.success(request, f"{'Nhập' if inv_type == 'IMPORT' else 'Xuất'} thành công.")
        return redirect('inventory:list')

class InventoryReportView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        flowers = FlowerItem.objects.all()
        report_data = []
        for f in flowers:
            total_import = Inventory.objects.filter(flower=f, type='IMPORT').aggregate(Sum('quantity'))['quantity__sum'] or 0
            total_export = Inventory.objects.filter(flower=f, type='EXPORT').aggregate(Sum('quantity'))['quantity__sum'] or 0
            stock = total_import - total_export
            report_data.append({
                'flower': f,
                'imported': total_import,
                'exported': total_export,
                'stock': stock,
                'low_stock': stock < 5,
            })
        total_stock = sum(item['stock'] for item in report_data)
        return render(request, 'inventory/inventory_report.html', {
            'report_data': report_data,
            'total_stock': total_stock,
        })


# ---------- GoodsReceipt (phiếu nhập theo nhà cung cấp) ----------
class GoodsReceiptListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = GoodsReceipt
    template_name = 'inventory/receipt_list.html'
    context_object_name = 'receipts'
    paginate_by = 20
    ordering = ['-created_at']

class GoodsReceiptDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = GoodsReceipt
    template_name = 'inventory/receipt_detail.html'
    context_object_name = 'receipt'
    pk_url_kwarg = 'receipt_id'

class GoodsReceiptCreateView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = GoodsReceiptForm()
        formset = GoodsReceiptItemFormSet()
        return render(request, 'inventory/receipt_form.html', {
            'form': form,
            'formset': formset,
            'empty_form': formset.empty_form,
            'formset_prefix': formset.prefix,
        })

    def post(self, request, *args, **kwargs):
        form = GoodsReceiptForm(request.POST, request.FILES)
        formset = GoodsReceiptItemFormSet(request.POST, request.FILES)
        if not form.is_valid() or not formset.is_valid():
            logger.debug("Receipt form errors: %s", form.errors)
            logger.debug("Receipt formset errors: %s", formset.errors)
            messages.error(request, "Dữ liệu không hợp lệ. Vui lòng kiểm tra các trường.")
            return render(request, 'inventory/receipt_form.html', {
                'form': form,
                'formset': formset,
                'empty_form': formset.empty_form,
                'formset_prefix': formset.prefix,
            })

        try:
            with transaction.atomic():
                receipt = form.save(commit=False)
                receipt.created_by = request.user
                receipt.save()

                total = Decimal('0')
                saved_items = []
                items = formset.save(commit=False)

                # handle deletions flagged in formset
                for obj in formset.deleted_objects:
                    obj.delete()

                # Pair forms and items so we can read hidden inputs per row
                form_item_pairs = []
                form_index = 0
                for form_row in formset.forms:
                    # skip forms marked for deletion
                    if form_row.cleaned_data.get('DELETE', False):
                        continue
                    # the corresponding instance is next from items list in order
                    instance = items[form_index]
                    form_item_pairs.append((form_row, instance))
                    form_index += 1

                for form_row, item in form_item_pairs:
                    # read hidden inputs rendered in template: item_app, item_model, item_id
                    prefix = form_row.prefix  # e.g. items-0
                    item_app = request.POST.get(f"{prefix}-item_app")
                    item_model = request.POST.get(f"{prefix}-item_model")
                    item_obj_id = request.POST.get(f"{prefix}-item_id")

                    if not item_app or not item_model or not item_obj_id:
                        raise ValueError("Thiếu thông tin vật phẩm ở một dòng.")

                    # set generic relation: find content type
                    ct = ContentType.objects.get(app_label=item_app, model=item_model.lower())
                    item.content_type = ct
                    item.object_id = int(item_obj_id)
                    item.receipt = receipt
                    item.save()
                    total += Decimal(item.total_price or 0)
                    saved_items.append(item)

                    # update stock on actual model (lock row)
                    Model = django_apps.get_model(item_app, item_model)
                    target = Model.objects.select_for_update().get(pk=item.object_id)
                    # update fields safely: prefer stock_bunches then stock
                    if hasattr(target, 'stock_bunches'):
                        target.stock_bunches = (target.stock_bunches or 0) + item.quantity_bunch
                    elif hasattr(target, 'stock'):
                        target.stock = (target.stock or 0) + item.quantity_bunch
                    else:
                        # if model doesn't have stock, just skip or log
                        logger.warning("Model %s.%s has no stock field.", item_app, item_model)
                    target.save()

                receipt.total_amount = total
                receipt.save()

        except (InvalidOperation, ValueError) as e:
            logger.exception("Lỗi khi tạo phiếu nhập")
            messages.error(request, f"Lỗi khi lưu phiếu: {e}")
            return render(request, 'inventory/receipt_form.html', {
                'form': form,
                'formset': formset,
                'empty_form': formset.empty_form,
                'formset_prefix': formset.prefix,
            })
        except Exception as e:
            logger.exception("Unexpected error saving GoodsReceipt")
            messages.error(request, "Có lỗi xảy ra khi lưu phiếu nhập. Liên hệ admin.")
            return render(request, 'inventory/receipt_form.html', {
                'form': form,
                'formset': formset,
                'empty_form': formset.empty_form,
                'formset_prefix': formset.prefix,
            })

        messages.success(request, "Đã tạo phiếu nhập thành công.")
        return redirect(reverse('inventory:receipts_detail', kwargs={'receipt_id': receipt.id}))

# ---------- API endpoints (class-based) ----------
class FlowerCategoryListAPI(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        qs = FlowerCategory.objects.order_by('name').values('id', 'name', 'slug')
        return JsonResponse(list(qs), safe=False)


class FlowersByCategoryAPI(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request, category_id, *args, **kwargs):
        qs = FlowerItem.objects.filter(category_id=category_id).values('id', 'name', 'stock_bunches', 'price')
        return JsonResponse(list(qs), safe=False)

# Các model category được phép quản lý ở đây (app_label, model_name, label hiển thị)
ALLOWED_CATEGORY_MODELS = [
    ('category', 'Category', 'Danh mục sản phẩm'),
    ('inventory', 'FlowerCategory', 'Danh mục hoa lẻ'),
    ('accessories', 'AccessoryCategory', 'Danh mục phụ kiện'),
]

# ----- Category manager -----
class CategoryManagerView(LoginRequiredMixin, StaffRequiredMixin, View):
    """
    Hiển thị danh sách tất cả category từ nhiều model, filter theo nguồn (app/model) và tìm kiếm theo tên.
    """
    template_name = 'inventory/manage_categories.html'

    def get_allowed_models(self):
        allowed = []
        for app_label, model_name, label in ALLOWED_CATEGORY_MODELS:
            try:
                model = django_apps.get_model(app_label, model_name)
                allowed.append((app_label, model_name, label, model))
            except LookupError:
                # ignore missing models (ví dụ accessories chưa tồn tại)
                continue
        return allowed

    def get(self, request):
        q = request.GET.get('q', '').strip()
        source = request.GET.get('source', '')  # source = "app_label.model_name" hoặc empty = tất cả
        allowed = self.get_allowed_models()
        results = []
        for app_label, model_name, label, model in allowed:
            qs = model.objects.all().order_by('id')
            if source and source != f"{app_label}.{model_name}":
                continue
            if q:
                qs = qs.filter(name__icontains=q)
            for obj in qs:
                results.append({
                    'app_label': app_label,
                    'model_name': model_name,
                    'label': label,
                    'id': obj.pk,
                    'name': getattr(obj, 'name', str(obj)),
                })
        # sort by label->name
        results = sorted(results, key=lambda r: (r['label'], r['name']))
        context = {
            'results': results,
            'allowed': [(f"{a}.{m}", lab) for a,m,lab,_ in allowed],
            'q': q,
            'source': source,
        }
        return render(request, self.template_name, context)

class CategoryCreateView(LoginRequiredMixin, StaffRequiredMixin, View):
    """
    Tạo category mới. User chọn nguồn (app_label + model_name) trong form.
    """
    template_name = 'inventory/category_form.html'

    def get(self, request):
        # show list of allowed models
        allowed = [(a,m,label) for a,m,label in ALLOWED_CATEGORY_MODELS if apps.is_installed(a)]
        return render(request, self.template_name, {'allowed': allowed, 'obj': None})

    def post(self, request):
        app_label = request.POST.get('app_label')
        model_name = request.POST.get('model_name')
        if not app_label or not model_name:
            messages.error(request, "Chọn loại danh mục.")
            return redirect('inventory:manage_categories')
        try:
            model = django_apps.get_model(app_label, model_name)
        except LookupError:
            messages.error(request, "Loại danh mục không hợp lệ.")
            return redirect('inventory:manage_categories')
        Form = modelform_factory(model, fields=['name'])
        form = Form(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã tạo danh mục mới.")
            return redirect('inventory:manage_categories')
        return render(request, self.template_name, {'form': form, 'allowed': [(app_label,model_name,model._meta.verbose_name)], 'obj': None})

class CategoryUpdateView(LoginRequiredMixin, StaffRequiredMixin, View):
    template_name = 'inventory/category_form.html'

    def dispatch(self, request, app_label, model_name, pk, *args, **kwargs):
        try:
            self.model = django_apps.get_model(app_label, model_name)
        except LookupError:
            raise Http404("Model không tồn tại.")
        self.obj = get_object_or_404(self.model, pk=pk)
        return super().dispatch(request, app_label, model_name, pk, *args, **kwargs)

    def get(self, request, app_label, model_name, pk):
        Form = modelform_factory(self.model, fields=['name'])
        form = Form(instance=self.obj)
        return render(request, self.template_name, {'form': form, 'obj': self.obj, 'allowed': [(app_label, model_name, self.model._meta.verbose_name)]})

    def post(self, request, app_label, model_name, pk):
        Form = modelform_factory(self.model, fields=['name'])
        form = Form(request.POST, instance=self.obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật danh mục.")
            return redirect('inventory:manage_categories')
        return render(request, self.template_name, {'form': form, 'obj': self.obj})

class CategoryDeleteView(LoginRequiredMixin, StaffRequiredMixin, View):
    template_name = 'inventory/category_confirm_delete.html'

    def dispatch(self, request, app_label, model_name, pk, *args, **kwargs):
        try:
            self.model = django_apps.get_model(app_label, model_name)
        except LookupError:
            raise Http404("Model không tồn tại.")
        self.obj = get_object_or_404(self.model, pk=pk)
        return super().dispatch(request, app_label, model_name, pk, *args, **kwargs)

    def get(self, request, app_label, model_name, pk):
        return render(request, self.template_name, {'obj': self.obj})

    def post(self, request, app_label, model_name, pk):
        # bạn có thể thêm kiểm tra ràng buộc nếu category có liên kết tới items
        try:
            self.obj.delete()
            messages.success(request, "Đã xóa danh mục.")
        except Exception as e:
            messages.error(request, f"Không thể xóa: {e}")
        return redirect('inventory:manage_categories')

# ----- API for dynamic item loading -----
class FlowerCategoryListAPI(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request):
        qs = FlowerCategory.objects.order_by('name').values('id','name')
        return JsonResponse(list(qs), safe=False)

class FlowersByCategoryAPI(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request, category_id):
        qs = FlowerItem.objects.filter(category_id=category_id).values('id','name','stock_bunches','price')
        return JsonResponse(list(qs), safe=False)

class ItemsByCategoryAPI(LoginRequiredMixin, StaffRequiredMixin, View):
    """
    Generic API: /api/items-by-category/<app_label>/<category_id>/
    - tries to find model 'Accessory' or 'AccessoryItem' under given app_label; returns id,name,stock if found.
    """
    def get(self, request, app_label, category_id):
        # try common accessory model names
        candidates = ['Accessory', 'AccessoryItem', 'Product']  # adjust if your app uses other model names
        for candidate in candidates:
            try:
                model = django_apps.get_model(app_label, candidate)
            except LookupError:
                continue
            # assume model has category_id and stock or stock_bunches fields
            qs = model.objects.filter(category_id=category_id).values('id','name','price')
            # try include stock fields if present
            out = []
            for o in qs:
                obj = model.objects.get(pk=o['id'])
                stock = None
                if hasattr(obj, 'stock'):
                    stock = getattr(obj, 'stock')
                elif hasattr(obj, 'stock_bunches'):
                    stock = getattr(obj, 'stock_bunches')
                o['stock'] = stock
                out.append(o)
            return JsonResponse(out, safe=False)
        raise Http404("No item model found for given app_label")