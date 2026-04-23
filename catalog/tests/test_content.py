from django.test import TestCase
from django.urls import reverse
from django.db.models.query import QuerySet
from catalog.models import Table, TableMaterial

class ContentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем два материала
        cls.mat_wood = TableMaterial.objects.create(name="Дерево")
        cls.mat_glass = TableMaterial.objects.create(name="Стекло")
        
        # ИЗМЕНЕНИЕ: Создаем столы в обратном/случайном порядке, чтобы убедиться, 
        # что тесты не зависят от порядка их добавления в БД.
        cls.table_c = Table.objects.create(
            brand="C_Wood_Mini", length=50.0, width=50.0, weight=5.0, material=cls.mat_wood
        )
        cls.table_b = Table.objects.create(
            brand="B_Glass_Table", length=90.0, width=90.0, weight=None, material=cls.mat_glass
        )
        cls.table_a = Table.objects.create(
            brand="A_Wood_Table", length=150.0, width=80.0, weight=25.0, material=cls.mat_wood
        )

    # TC-02: Список содержит объекты
    def test_list_context_objects_not_empty(self):
        response = self.client.get(reverse('catalog:table_list'))
        self.assertIn('tables', response.context)
        # Проверяем, что передается именно QuerySet
        self.assertIsInstance(response.context['tables'], QuerySet)
        # Динамически проверяем количество (тест не упадет, если добавить 4-й стол)
        expected_count = Table.objects.count()
        self.assertEqual(len(response.context['tables']), expected_count)

    # TC-03: Фильтрация по типу
    def test_list_filter_by_type_expected(self):
        url = reverse('catalog:table_list')
        # Передаем query-параметр ?type=ID_Дерева
        response = self.client.get(url, {'type': self.mat_wood.pk})
        tables = response.context['tables']
        
        # Динамически считаем количество деревянных столов в БД
        expected_count = Table.objects.filter(material=self.mat_wood).count()
        self.assertEqual(len(tables), expected_count)
        
        for table in tables:
            self.assertEqual(table.material, self.mat_wood)

    # TC-04 (контекст): Детальная страница содержит нужный объект
    def test_detail_context_contains_object(self):
        url = reverse('catalog:table_detail', args=[self.table_a.pk])
        response = self.client.get(url)
        self.assertIn('table', response.context)
        self.assertEqual(response.context['table'].brand, self.table_a.brand)

    # TC-07: About содержит текст
    def test_about_contains_text_expected(self):
        response = self.client.get(reverse('catalog:about'))
        self.assertContains(response, "О проекте", status_code=200)

    # TC-08: Пустой список товаров
    def test_list_empty_expected(self):
        Table.objects.all().delete() # Очищаем столы
        response = self.client.get(reverse('catalog:table_list'))
        self.assertEqual(len(response.context['tables']), 0)
        self.assertContains(response, "Товаров пока нет")

    # TC-10: Контекст имеет нужные ключи
    def test_list_context_keys_exist(self):
        response = self.client.get(reverse('catalog:table_list'))
        self.assertIn('tables', response.context)
        self.assertIn('types', response.context)
        self.assertIsInstance(response.context['types'], QuerySet)

    # ДОП. ТЕСТ: Сортировка по умолчанию (по бренду)
    def test_list_sort_default_by_brand(self):
        response = self.client.get(reverse('catalog:table_list'))
        tables = list(response.context['tables'])
        
        # Извлекаем все бренды и проверяем, что они отсортированы по алфавиту.
        # Тест пройдет, даже если добавится "BB_Glass_Table".
        brands = [t.brand for t in tables]
        self.assertEqual(brands, sorted(brands))

    # ДОП. ТЕСТ: Сортировка по обязательному атрибуту (Длина)
    def test_list_sort_by_required_attr_length(self):
        # ?sort=length
        response = self.client.get(reverse('catalog:table_list'), {'sort': 'length'})
        tables = list(response.context['tables'])
        
        # Извлекаем длины и проверяем, что список идет по возрастанию
        lengths = [t.length for t in tables]
        self.assertEqual(lengths, sorted(lengths))

    # ДОП. ТЕСТ: Сортировка по НЕобязательному атрибуту (Вес)
    def test_list_sort_by_optional_attr_weight(self):
        # ?sort=weight
        response = self.client.get(reverse('catalog:table_list'), {'sort': 'weight'})
        tables = list(response.context['tables'])
        
        # Проверяем, что элементы с заполненным весом отсортированы правильно,
        # игнорируя позиции NULL-значений (они зависят от БД)
        weights = [t.weight for t in tables if t.weight is not None]
        self.assertEqual(weights, sorted(weights))
        
    def test_list_sort_by_type(self):
        # Если передать неразрешенное поле для сортировки (?sort=material__name),
        # view должно применить fall-back поведение (сортировку по бренду).
        response = self.client.get(reverse('catalog:table_list'), {'sort': 'material__name'})
        tables = list(response.context['tables'])
        
        # Убеждаемся, что сработало default-поведение и список отсортирован по алфавиту марок
        brands = [t.brand for t in tables]
        self.assertEqual(brands, sorted(brands))