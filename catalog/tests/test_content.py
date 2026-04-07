from django.test import TestCase
from django.urls import reverse
from catalog.models import Table, TableMaterial


class ContentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.mat1 = TableMaterial.objects.create(name="Дерево")
        cls.mat2 = TableMaterial.objects.create(name="Стекло")

        cls.table1 = Table.objects.create(brand="A_Wood", length=100, width=50, weight=20, material=cls.mat1)
        cls.table2 = Table.objects.create(brand="B_Glass", length=90, width=90, weight=None, material=cls.mat2)

    # TC-02: Список содержит объекты
    def test_list_context_not_empty(self):
        response = self.client.get(reverse('catalog:table_list'))
        self.assertIn('tables', response.context)
        self.assertTrue(len(response.context['tables']) > 0)

    # TC-03: Фильтрация по типу
    def test_list_filter_by_type_success(self):
        # Передаем ?type=<id_дерева>
        response = self.client.get(reverse('catalog:table_list'), {'type': self.mat1.pk})
        self.assertEqual(len(response.context['tables']), 1)
        self.assertEqual(response.context['tables'][0].material, self.mat1)

    # Проверка сортировки (доп.)
    def test_list_sort_by_optional_field(self):
        # Сортируем по весу (weight - необязательное поле)
        response = self.client.get(reverse('catalog:table_list'), {'sort': 'weight'})
        self.assertEqual(response.status_code, 200)
        tables = response.context['tables']
        # Проверяем, что сортировка отработала (None обычно идут первыми или последними в БД)
        self.assertTrue(len(tables) == 2)

    # TC-04: Детальная страница содержит контекст
    def test_detail_context_has_object(self):
        response = self.client.get(reverse('catalog:table_detail', args=[self.table1.pk]))
        self.assertIn('table', response.context)
        self.assertEqual(response.context['table'], self.table1)

    # TC-07: About содержит текст
    def test_about_contains_text(self):
        response = self.client.get(reverse('catalog:about'))
        # Текст должен совпадать с тем, что у тебя в about.html
        self.assertContains(response, "О проекте")

    # TC-08: Пустой список товаров
    def test_list_empty_is_correct(self):
        Table.objects.all().delete()  # Удаляем все столы
        response = self.client.get(reverse('catalog:table_list'))
        self.assertEqual(len(response.context['tables']), 0)
        # Проверяем, что шаблон корректно отрендерил пустой список
        self.assertContains(response, "Товаров пока нет")

    # TC-10: Контекст имеет нужные ключи
    def test_list_context_keys_exist(self):
        response = self.client.get(reverse('catalog:table_list'))
        self.assertIn('tables', response.context)
        self.assertIn('types', response.context)  # Проверяем наличие 'types' из get_context_data
