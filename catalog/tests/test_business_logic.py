from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from catalog.models import Table, TableMaterial, Order, OrderItem

class BusinessLogicTests(TestCase):
    def setUp(self):
        # 1. Создаем роли (пользователей) БЕЗ паролей
        self.guest = User.objects.create_user(username='guest')
        self.merchandiser = User.objects.create_user(username='merchandiser')
        self.manager1 = User.objects.create_user(username='manager1')
        self.manager2 = User.objects.create_user(username='manager2')
        
        # Даем товароведу права
        add_perm = Permission.objects.get(codename='add_table')
        change_perm = Permission.objects.get(codename='change_table')
        self.merchandiser.user_permissions.add(add_perm, change_perm)
        
        # Даем менеджерам права
        add_order_perm = Permission.objects.get(codename='add_order')
        view_order_perm = Permission.objects.get(codename='view_order')
        self.manager1.user_permissions.add(add_order_perm, view_order_perm)
        self.manager2.user_permissions.add(add_order_perm, view_order_perm)

        # 2. Создаем товар (оставлено без изменений)
        self.material = TableMaterial.objects.create(name="Дерево")
        self.table = Table.objects.create(
            brand="BusinessTable", length=100, width=50, material=self.material,
            price=1000, 
            small_wholesale_price=900, small_wholesale_threshold=10,
            large_wholesale_price=800, large_wholesale_threshold=50
        )

    # --- ТЕСТ 2: Разграничение прав пользователей (Товаровед) ---
    def test_merchandiser_can_create_table(self):
        """Товаровед имеет права add_table и может зайти на страницу добавления"""
        # Используем force_login вместо обычного login
        self.client.force_login(self.merchandiser)
        response = self.client.get(reverse('catalog:table_add'))
        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_create_table(self):
        """Менеджер не имеет прав add_table и получит 403 Forbidden"""
        self.client.force_login(self.manager1)
        response = self.client.get(reverse('catalog:table_add'))
        self.assertEqual(response.status_code, 403)

    # --- ТЕСТ 3: Изоляция менеджеров ---
    def test_manager_order_isolation(self):
        """Менеджер 1 не видит партию Менеджера 2"""
        Order.objects.create(manager=self.manager1)
        
        self.client.force_login(self.manager2)
        response = self.client.get(reverse('catalog:my_orders'))
        
        self.assertEqual(len(response.context['orders']), 0)

    # ...остальные тесты...