from django.views.generic import ListView, DetailView, TemplateView
from .models import Table, TableMaterial

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