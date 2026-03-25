from django.urls import path
from .views import TableListView, TableDetailView, AboutView

app_name = 'catalog'

urlpatterns = [
    path('', TableListView.as_view(), name='table_list'),
    path('table/<int:pk>/', TableDetailView.as_view(), name='table_detail'),
    path('about/', AboutView.as_view(), name='about'),
]