from django.db import models

class Table(models.Model):
    MATERIAL_CHOICES = [
        ('дерево', 'Дерево'),
        ('стекло', 'Стекло'),
        ('металл', 'Металл'),
        ('пластик', 'Пластик'),
    ]

    brand = models.CharField(max_length=100, verbose_name="Марка")
    is_foldable = models.BooleanField(default=False, verbose_name="Складной")
    length = models.FloatField(verbose_name="Длина (см)")
    width = models.FloatField(verbose_name="Ширина (см)")
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, verbose_name="Материал")
    weight = models.FloatField(null=True, blank=True, verbose_name="Вес (кг)")

    @property
    def table_area(self) -> float:
        """Вычисляемое свойство: площадь столешницы."""
        return self.length * self.width

    def __str__(self):
        return f"Стол {self.brand} ({self.material})"

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"