from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# Кастомный менеджер (Требования 6 и 7)
class TableManager(models.Manager):
    def by_material(self, material_name):
        """Возвращает столы только определенного материала"""
        return self.filter(material__name=material_name)

    def heavy_tables(self):
        """Возвращает только тяжелые столы (весом больше 20 кг)"""
        return self.filter(weight__gt=20.0)


class TableMaterial(models.Model):
    """Отдельная таблица для типа/материала (Связь один-ко-многим)"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Материал")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"


class Table(models.Model):
    # Поля с валидаторами (для Тестов 1 и 2)
    brand = models.CharField(max_length=100, unique=True, verbose_name="Марка") # unique для теста 2
    is_foldable = models.BooleanField(default=False, verbose_name="Складной")
    
    # MinValueValidator для проверки на уровне Python (Тест 1)
    length = models.FloatField(validators=[MinValueValidator(0.1)], verbose_name="Длина (см)")
    width = models.FloatField(validators=[MinValueValidator(0.1)], verbose_name="Ширина (см)")
    
    # Связь с таблицей материалов. on_delete=models.PROTECT (Тест 3)
    material = models.ForeignKey(TableMaterial, on_delete=models.PROTECT, verbose_name="Материал")
    
    weight = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.1)], verbose_name="Вес (кг)")

    # Подключаем кастомный менеджер
    objects = TableManager()

    # 1-е Вычисляемое свойство (Тест 4)
    @property
    def table_area(self) -> float:
        return self.length * self.width

    # 2-е Вычисляемое свойство (Тест 5)
    @property
    def is_heavy(self) -> bool:
        if self.weight:
            return self.weight > 20.0
        return False

    def __str__(self):
        return f"Стол {self.brand}"

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"
        # Constraint на уровне БД (Тест 8). Нельзя сохранить отрицательную длину даже в обход валидаторов
        constraints = [
            models.CheckConstraint(check=models.Q(length__gt=0), name='check_positive_length'),
            models.CheckConstraint(check=models.Q(width__gt=0), name='check_positive_width'),
        ]