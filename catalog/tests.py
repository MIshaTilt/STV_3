from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from .models import Table

class CatalogSeleniumTests(LiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Инициализируем браузер (Убедись, что установлен ChromeDriver)
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Создаем тестовый стол в тестовой БД, чтобы было что открывать
        self.table = Table.objects.create(
            brand="IKEA Bjursta",
            is_foldable=True,
            length=140.0,
            width=84.0,
            material="дерево",
            weight=25.0
        )

    def test_navigation_to_about_page(self):
        """Тест 1 из лекции: Переход со страницы списка на страницу 'О проекте'"""
        self.selenium.get(self.live_server_url) # Открываем главную (список)
        
        # Находим ссылку "О проекте" по ID и кликаем
        about_link = self.selenium.find_element(By.ID, "about-link")
        about_link.click()
        
        # Проверяем, что мы оказались на странице "О проекте"
        # Ищем заголовок на новой странице
        about_title = self.selenium.find_element(By.ID, "about-title")
        self.assertEqual(about_title.text, "О проекте")

    def test_detail_page_has_h1_tag(self):
        """Тест 2 (свой): Поиск тега H1 на странице детального описания"""
        # Переходим на страницу созданного в setUp стола
        self.selenium.get(f"{self.live_server_url}/table/{self.table.pk}/")
        
        # Пытаемся найти тег h1
        try:
            h1_element = self.selenium.find_element(By.TAG_NAME, "h1")
            is_found = True
            text = h1_element.text
        except Exception:
            is_found = False
            text = ""

        # Проверяем, что тег найден, иначе карточка не верна (по условию)
        self.assertTrue(is_found, "Тег H1 не найден. Карточка товара не верна!")
        self.assertIn(self.table.brand, text)