from django.urls import path
from .views import (TableListView, TableDetailView, AboutView,
                    TableCreateView, TableUpdateView, ManagerOrderListView, AddToCartView)

app_name = 'catalog'

urlpatterns = [
    path('', TableListView.as_view(), name='table_list'),
    path('table/<int:pk>/', TableDetailView.as_view(), name='table_detail'),
    path('about/', AboutView.as_view(), name='about'),

    path('table/add/', TableCreateView.as_view(), name='table_add'),
    path('table/<int:pk>/edit/', TableUpdateView.as_view(), name='table_edit'),
    path('my-orders/', ManagerOrderListView.as_view(), name='my_orders'),
    path('add-to-cart/<int:table_id>/', AddToCartView.as_view(), name='add_to_cart'),
]
