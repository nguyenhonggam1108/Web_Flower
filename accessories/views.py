from django.views.generic import ListView, DetailView
from django.views import View
from django.http import JsonResponse, Http404
from .models import AccessoryCategory, AccessoryItem

class AccessoryListView(ListView):
    model = AccessoryItem
    template_name = 'accessories/list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('category')
        q = self.request.GET.get('q')
        cat = self.request.GET.get('category')
        if q:
            qs = qs.filter(name__icontains=q)
        if cat:
            qs = qs.filter(category_id=cat)
        return qs.order_by('-created_at')

class AccessoryDetailView(DetailView):
    model = AccessoryItem
    template_name = 'accessories/detail.html'
    context_object_name = 'item'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

class AccessoryCategoryListAPI(View):
    def get(self, request):
        qs = AccessoryCategory.objects.order_by('name').values('id','name')
        return JsonResponse(list(qs), safe=False)

class AccessoryItemsByCategoryAPI(View):
    def get(self, request, category_id):
        qs = AccessoryItem.objects.filter(category_id=category_id).values('id','name','price','stock','slug')
        return JsonResponse(list(qs), safe=False)