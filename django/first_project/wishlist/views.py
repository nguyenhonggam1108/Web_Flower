from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from product.models import Product
from wishlist.models import Wishlist


# 🔹 1. Thêm / xóa yêu thích (AJAX)
class ToggleWishlistView(LoginRequiredMixin, View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        if not product_id:
            return JsonResponse({'error': 'Thiếu product_id'}, status=400)

        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user, product=product
        )

        if not created:
            wishlist_item.delete()
            return JsonResponse({'status': 'removed', 'message': 'Đã xóa khỏi danh sách yêu thích'})
        return JsonResponse({'status': 'added', 'message': 'Đã thêm vào danh sách yêu thích'})


# 🔹 2. Lấy danh sách yêu thích (AJAX)
class GetWishlistView(LoginRequiredMixin, View):
    def get(self, request):
        wishlist = Wishlist.objects.filter(user=request.user).select_related('product')
        data = [
            {
                'id': w.product.id,
                'name': w.product.name,
                'image': w.product.image.url if w.product.image else '',
                'price': w.product.price,
            }
            for w in wishlist
        ]
        return JsonResponse({'wishlist': data})


# 🔹 3. Kiểm tra trạng thái yêu thích của sản phẩm
class WishlistStatusView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        exists = Wishlist.objects.filter(user=request.user, product_id=product_id).exists()
        return JsonResponse({'liked': exists})


# 🔹 4. Trang danh sách yêu thích (HTML)
class WishlistPageView(LoginRequiredMixin, TemplateView):
    template_name = "wishlist/wishlist_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wishlist = Wishlist.objects.filter(user=self.request.user).select_related("product")
        context["wishlist_items"] = wishlist
        return context


# 🔹 5. Xóa sản phẩm khỏi danh sách yêu thích (form POST)
class RemoveFromWishlistView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
        return redirect('wishlist:wishlist_page')
