from django.test import TestCase
from django.urls import reverse
from catalog.models import Table, TableMaterial


class RoutesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.material = TableMaterial.objects.create(name="Дерево")
        cls.table = Table.objects.create(brand="TestRouteTable", length=100, width=50, material=cls.material)

    # TC-01: Главная страница каталога
    def test_list_status_200(self):
        url = reverse('catalog:table_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/table_list.html')

    # TC-04 (часть): Детальная страница - доступность
    def test_detail_status_200(self):
        url = reverse('catalog:table_detail', args=[self.table.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # TC-05: Несуществующий товар
    def test_detail_999_404(self):
        url = reverse('catalog:table_detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # TC-06: Страница About
    def test_about_status_200(self):
        url = reverse('catalog:about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/about.html')

    # TC-09: URL через reverse()
    def test_list_reverse_matches_url(self):
        url = reverse('catalog:table_list')
        # Если в urls.py у тебя path('', TableListView...), то url будет '/'
        self.assertEqual(url, '/')
