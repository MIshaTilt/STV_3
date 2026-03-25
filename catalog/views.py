from django.views.generic import ListView, DetailView, TemplateView
from .models import Table

# 1. Список товара (домашняя страничка)
class TableListView(ListView):
    model = Table
    template_name = 'catalog/table_list.html'
    context_object_name = 'tables'

# 2. Детальное описание товара
class TableDetailView(DetailView):
    model = Table
    template_name = 'catalog/table_detail.html'
    context_object_name = 'table'

# 3. Страничка о сервисе
class AboutView(TemplateView):
    template_name = 'catalog/about.html'