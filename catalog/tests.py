from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db.models import ProtectedError
from .models import Table, TableMaterial

class TableModelTest(TestCase):

    # ТЕСТ 9: Правильное использование setUpTestData
    # Выполняется 1 раз для всего класса. Отлично подходит для статических данных,
    # которые не меняются (например, справочник материалов).
    @classmethod
    def setUpTestData(cls):
        cls.material_wood = TableMaterial.objects.create(name="Дерево")
        cls.material_glass = TableMaterial.objects.create(name="Стекло")

    # ТЕСТ 10: Правильное использование setUp
    # Выполняется перед КАЖДЫМ тестом. Подходит для объектов, которые мы будем 
    # изменять, удалять или тестировать в рамках конкретного метода.
    def setUp(self):
        self.table_standard = Table.objects.create(
            brand="IKEA Basic",
            length=120.0,
            width=60.0,
            weight=15.0,
            material=self.material_wood
        )

    # ТЕСТ 9 (как отдельный тест): Проверка правильного использования setUpTestData
    def test_setup_test_data_works(self):
        """Проверяет, что статические данные (материалы) успешно загружены 1 раз для всего класса"""
        materials_count = TableMaterial.objects.count()
        self.assertEqual(materials_count, 2)
        self.assertEqual(self.material_wood.name, "Дерево")

    # ТЕСТ 10 (как отдельный тест): Проверка правильного использования setUp
    def test_setup_works(self):
        """Проверяет, что setUp корректно создает свежий объект стола перед этим тестом"""
        self.assertEqual(self.table_standard.brand, "IKEA Basic")
        self.assertEqual(self.table_standard.material.name, "Дерево")

    # ТЕСТ 1: Валидация положительного числа (Поле)
    def test_positive_number_validation(self):
        table = Table(
            brand="Bad Table",
            length=-10.0,  # Отрицательное число!
            width=50.0,
            material=self.material_wood
        )
        with self.assertRaises(ValidationError):
            table.full_clean() # Метод запускает Python-валидаторы поля

    # ТЕСТ 2: Валидация уникальности (название марки)
    def test_unique_brand_validation(self):
        table_duplicate = Table(
            brand="IKEA Basic", # Такое имя уже создано в setUp!
            length=100.0,
            width=50.0,
            material=self.material_glass
        )
        with self.assertRaises(ValidationError):
            table_duplicate.full_clean()

    # ТЕСТ 3: on_delete=PROTECT для типа товара (Связь)
    def test_on_delete_protect(self):
        # Пытаемся удалить материал "Дерево", к которому привязан table_standard
        with self.assertRaises(ProtectedError):
            self.material_wood.delete()

    # ТЕСТ 4: Вычисляемое свойство 1 (Площадь)
    def test_property_table_area(self):
        # 120 * 60 = 7200
        self.assertEqual(self.table_standard.table_area, 7200.0)

    # ТЕСТ 5: Вычисляемое свойство 2 (Тяжелый стол)
    def test_property_is_heavy(self):
        self.assertFalse(self.table_standard.is_heavy) # Вес 15, значит False
        
        heavy_table = Table.objects.create(
            brand="Massive Oak",
            length=200.0, width=100.0, weight=45.0,
            material=self.material_wood
        )
        self.assertTrue(heavy_table.is_heavy) # Вес 45, значит True

    # ТЕСТ 6: Менеджер by_material()
    def test_manager_by_material(self):
        Table.objects.create(brand="Glassy", length=100, width=100, material=self.material_glass)
        
        wood_tables = Table.objects.by_material("Дерево")
        glass_tables = Table.objects.by_material("Стекло")
        
        self.assertEqual(wood_tables.count(), 1)
        self.assertEqual(glass_tables.count(), 1)
        self.assertEqual(wood_tables.first().brand, "IKEA Basic")

    # ТЕСТ 7: Второй менеджер heavy_tables()
    def test_manager_heavy_tables(self):
        Table.objects.create(
            brand="Heavy Metal", length=100, width=100, weight=50.0, material=self.material_wood
        )
        heavy_tables = Table.objects.heavy_tables()
        
        self.assertEqual(heavy_tables.count(), 1)
        self.assertEqual(heavy_tables.first().brand, "Heavy Metal")

    # ТЕСТ 8: CheckConstraint на уровне БД
    def test_check_constraint_db_level(self):
        # Сохраняем напрямую в БД (минуя full_clean валидаторы Python)
        with self.assertRaises(IntegrityError):
            Table.objects.create(
                brand="Direct DB Fail",
                length=-5.0, # Нарушает CheckConstraint
                width=50.0,
                material=self.material_wood
            )