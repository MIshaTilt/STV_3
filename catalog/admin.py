from django.contrib import admin
from .models import Table, TableMaterial


@admin.register(TableMaterial)
class TableMaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('brand', 'material', 'length', 'width', 'weight', 'is_foldable')
    list_filter = ('material', 'is_foldable')
