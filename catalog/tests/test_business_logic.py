from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from catalog.models import Table, TableMaterial, Order, OrderItem

class BusinessLogicTests(TestCase):
    def setUp(self):
        # 1. Создаем роли (пользователей)
        self.guest = User.objects.create_user(username='guest', password='123')
        
        self.merchandiser = User.objects.create_user(username='merchandiser', password='123')
        # Даем товароведу права на изменение столов
        add_perm = Permission.objects.get(codename='add_table')
        change_perm = Permission.objects.get(codename='change_table')
        self.merchandiser.user_permissions.add(add_perm, change_perm)
        
        self.manager1 = User.objects.create_user(username='manager1', password='123')
        self.manager2 = User.objects.create_user(username='manager2', password='123')
        
        add_order_perm = Permission.objects.get(codename='add_order')
        view_order_perm = Permission.objects.get(codename='view_order')
        self.manager1.user_permissions.add(add_order_perm, view_order_perm)
        self.manager2.user_permissions.add(add_order_perm, view_order_perm)

        # 2. Создаем товар
        self.material = TableMaterial.objects.create(name="Дерево")
        self.table = Table.objects.create(
            brand="BusinessTable", length=100, width=50, material=self.material,
            price=1000, 
            small_wholesale_price=900, small_wholesale_threshold=10,
            large_wholesale_price=800, large_wholesale_threshold=50
        )

    # --- ТЕСТ 1: Гость может только просматривать ---
    def test_guest_read_only(self):
        """Гость может зайти на список, но при попытке добавить товар получит 403 Forbidden или редирект на логин"""
        # Успешный просмотр
        response = self.client.get(reverse('catalog:table_list'))
        self.assertEqual(response.status_code, 200)
        
        # Попытка зайти на создание товара без логина (будет редирект 302 на страницу логина)
        response_add = self.client.get(reverse('catalog:table_add'))
        self.assertEqual(response_add.status_code, 302)

    # --- ТЕСТ 2: Разграничение прав пользователей (Товаровед) ---
    def test_merchandiser_can_create_table(self):
        """Товаровед имеет права add_table и может зайти на страницу добавления"""
        self.client.login(username='merchandiser', password='123')
        response = self.client.get(reverse('catalog:table_add'))
        self.assertEqual(response.status_code, 200) # Доступ разрешен

    def test_manager_cannot_create_table(self):
        """Менеджер не имеет прав add_table и получит 403 Forbidden"""
        self.client.login(username='manager1', password='123')
        response = self.client.get(reverse('catalog:table_add'))
        self.assertEqual(response.status_code, 403) # Доступ запрещен

    # --- ТЕСТ 3: Изоляция менеджеров (один не видит чужую партию) ---
    def test_manager_order_isolation(self):
        """Менеджер 1 не видит партию Менеджера 2"""
        # Создаем партию для Менеджера 1
        Order.objects.create(manager=self.manager1)
        
        # Заходим под Менеджером 2
        self.client.login(username='manager2', password='123')
        response = self.client.get(reverse('catalog:my_orders'))
        
        # Проверяем, что список партий для менеджера 2 пуст
        self.assertEqual(len(response.context['orders']), 0)

    # --- ТЕСТ 4: Корректное изменение объектов каталога ---
    def test_table_price_modification(self):
        """Проверка, что объект каталога (товар) успешно меняет цену в БД"""
        self.table.price = 1200
        self.table.save()
        self.table.refresh_from_db()
        self.assertEqual(self.table.price, 1200)

    # --- ТЕСТ 5: Корректный расчёт суммы партии товара (с оптом и скидкой) ---
    def test_cart_calculation_logic(self):
        """
        Проверка расчетов:
        1 шт = 1000 руб
        10 шт (мелкий опт 900) = 9000 руб
        50 шт (крупный опт 800) = 40000 руб
        Если общая сумма > 50000 руб, применяется скидка 5%
        """
        order = Order.objects.create(manager=self.manager1)
        
        # 1. Позиция без опта (5 шт * 1000 = 5000)
        item1 = OrderItem.objects.create(order=order, table=self.table, quantity=5)
        self.assertEqual(item1.get_cost(), 5000)

        # 2. Позиция мелкий опт (10 шт * 900 = 9000)
        item2 = OrderItem.objects.create(order=order, table=self.table, quantity=10)
        self.assertEqual(item2.get_cost(), 9000)

        # 3. Позиция крупный опт (50 шт * 800 = 40000)
        item3 = OrderItem.objects.create(order=order, table=self.table, quantity=50)
        self.assertEqual(item3.get_cost(), 40000)

        # 4. Общая сумма: 5000 + 9000 + 40000 = 54000
        self.assertEqual(order.total_base_cost, 54000)

        # 5. Итоговая со скидкой (54000 > 50000, скидка 5% = 51300)
        self.assertEqual(order.final_total, 51300)

    def test_add_to_cart_view(self):
        """Проверка работы URL-эндпоинта 'Добавить в корзину'"""
        self.client.login(username='manager1', password='123')
        
        # Делаем клик по ссылке "В корзину" (GET-запрос)
        response = self.client.get(reverse('catalog:add_to_cart', args=[self.table.pk]))
        
        # Проверяем редирект обратно в каталог (код 302)
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что корзина создалась и товар там есть
        order = Order.objects.get(manager=self.manager1)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().table, self.table)
        self.assertEqual(order.items.first().quantity, 1)

        # "Кликаем" второй раз - количество должно стать 2
        self.client.get(reverse('catalog:add_to_cart', args=[self.table.pk]))
        self.assertEqual(order.items.first().quantity, 2)

    def test_manager_cannot_edit_table(self):
        """Менеджер пытается зайти на URL редактирования товара (удел товароведа)"""
        self.client.login(username='manager1', password='123')
        
        # Пытаемся зайти на форму редактирования
        response = self.client.get(reverse('catalog:table_edit', args=[self.table.pk]))
        
        # Ожидаем 403 Forbidden, так как нет права change_table
        self.assertEqual(response.status_code, 403)

    # --- ТЕСТ 9: Товаровед НЕ имеет корзины ---
    def test_merchandiser_cannot_access_cart(self):
        """Товаровед пытается зайти в свои партии или добавить товар в корзину"""
        self.client.login(username='merchandiser', password='123')
        
        # Пытаемся зайти в список заказов
        response_orders = self.client.get(reverse('catalog:my_orders'))
        self.assertEqual(response_orders.status_code, 403) # Доступ закрыт
        
        # Пытаемся добавить товар в корзину
        response_add_cart = self.client.get(reverse('catalog:add_to_cart', args=[self.table.pk]))
        self.assertEqual(response_add_cart.status_code, 403) # Доступ закрыт

