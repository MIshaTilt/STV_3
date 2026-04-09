from django.test import TestCase
from django.urls import reverse
from catalog.models import Table, TableMaterial

class RoutesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Подготовка данных для тестов маршрутов
        cls.material = TableMaterial.objects.create(name="Дерево")
        cls.table = Table.objects.create(
            brand="RouteTestBrand", length=100.0, width=50.0, material=cls.material
        )

    # TC-01: Главная страница каталога
    def test_list_status_200_expected(self):
        url = reverse('catalog:table_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/table_list.html')

    # TC-04 (маршрут): Детальная страница
    def test_detail_status_200_expected(self):
        url = reverse('catalog:table_detail', args=[self.table.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/table_detail.html')

    # TC-05: Несуществующий товар
    def test_detail_404_if_not_exists(self):
        url = reverse('catalog:table_detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # TC-06: Страница About
    def test_about_status_200_expected(self):
        url = reverse('catalog:about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/about.html')

    # TC-09: URL через reverse()
    def test_list_reverse_match_url(self):
        url = reverse('catalog:table_list')
        # В зависимости от твоего config/urls.py, путь может быть '/' или '/products/'
        # Замени '/' на то, что у тебя реально используется
        self.assertEqual(url, '/')