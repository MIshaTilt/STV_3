from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Table, TableMaterial, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

class TableListView(ListView):
    model = Table
    template_name = 'catalog/table_list.html'
    context_object_name = 'tables' # В задании 'products', у нас логично 'tables'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 1. Фильтрация по полю типа (материала) через GET-параметр ?type=1
        material_type = self.request.GET.get('type')
        if material_type:
            queryset = queryset.filter(material_id=material_type)
            
        # 2. Сортировка списка
        sort_by = self.request.GET.get('sort')
        # Разрешенные поля: бренд, длина, вес (необязательное поле)
        if sort_by in ['brand', 'length', 'weight']:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('brand') # Сортировка по алфавиту по умолчанию
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем типы для TC-10
        context['types'] = TableMaterial.objects.all()
        return context

class TableDetailView(DetailView):
    model = Table
    template_name = 'catalog/table_detail.html'
    context_object_name = 'table' # В задании 'product'

class AboutView(TemplateView):
    template_name = 'catalog/about.html'

# --- VIEWS ТОВАРОВЕДА ---
class TableCreateView(PermissionRequiredMixin, CreateView):
    model = Table
    fields = '__all__'
    template_name = 'catalog/table_form.html'
    success_url = reverse_lazy('catalog:table_list')
    # Проверка роли: только пользователи с правом добавления стола
    permission_required = 'catalog.add_table' 

class TableUpdateView(PermissionRequiredMixin, UpdateView):
    model = Table
    fields = '__all__'
    template_name = 'catalog/table_form.html'
    success_url = reverse_lazy('catalog:table_list')
    permission_required = 'catalog.change_table'

class ManagerOrderListView(PermissionRequiredMixin, ListView):
    """Список партий доступен ТОЛЬКО тем, у кого есть право view_order (Менеджерам)"""
    model = Order
    template_name = 'catalog/order_list.html'
    context_object_name = 'orders'
    permission_required = 'catalog.view_order' # <--- Строгая проверка роли

    def get_queryset(self):
        return Order.objects.filter(manager=self.request.user)

class AddToCartView(PermissionRequiredMixin, View):
    """Добавление в корзину доступно ТОЛЬКО тем, у кого есть право add_order"""
    permission_required = 'catalog.add_order' # <--- Строгая проверка роли
    
    def get(self, request, table_id):
        table = get_object_or_404(Table, id=table_id)
        order, created = Order.objects.get_or_create(manager=request.user)
        order_item, item_created = OrderItem.objects.get_or_create(order=order, table=table)
        
        if not item_created:
            order_item.quantity += 1
            order_item.save()
            
        return redirect('catalog:table_list')

