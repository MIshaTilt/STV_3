from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

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
    # ... (старые поля оставляем: brand, is_foldable, length, width, material, weight) ...
    brand = models.CharField(max_length=100, unique=True, verbose_name="Марка")
    is_foldable = models.BooleanField(default=False, verbose_name="Складной")
    length = models.FloatField(validators=[MinValueValidator(0.1)], verbose_name="Длина (см)")
    width = models.FloatField(validators=[MinValueValidator(0.1)], verbose_name="Ширина (см)")
    material = models.ForeignKey('TableMaterial', on_delete=models.PROTECT, verbose_name="Материал")
    weight = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.1)], verbose_name="Вес (кг)")

    # НОВЫЕ ПОЛЯ (Цены и опт)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00, verbose_name="Цена за 1 шт")
    
    small_wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, default=950.00, verbose_name="Цена (мелкий опт)")
    small_wholesale_threshold = models.PositiveIntegerField(default=10, verbose_name="Мелкий опт от (шт)")
    
    large_wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, default=900.00, verbose_name="Цена (крупный опт)")
    large_wholesale_threshold = models.PositiveIntegerField(default=50, verbose_name="Крупный опт от (шт)")

    objects = TableManager() # Из прошлой практики

    @property
    def table_area(self) -> float:
        return self.length * self.width

    @property
    def is_heavy(self) -> bool:
        return self.weight > 20.0 if self.weight else False

    def __str__(self):
        return f"Стол {self.brand}"

# НОВЫЕ МОДЕЛИ ДЛЯ КОРЗИНЫ / ПАРТИИ

class Order(models.Model):
    """Партия товара (Корзина), закрепленная за менеджером"""
    manager = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Менеджер")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    @property
    def total_base_cost(self):
        """Сумма партии до применения глобальной скидки"""
        return sum(item.get_cost() for item in self.items.all())

    @property
    def final_total(self):
        """Итоговая сумма с учетом дополнительной скидки на общую сумму (Творческое задание)"""
        total = self.total_base_cost
        # Например: если заказ больше 50 000 руб, даем еще 5% скидки сверху
        if total > 50000:
            return float(total) * 0.95 
        return float(total)

    def __str__(self):
        return f"Партия #{self.id} (Менеджер: {self.manager.username})"

class OrderItem(models.Model):
    """Позиция в партии"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def get_cost(self):
        """Расчет стоимости позиции с учетом оптовых порогов"""
        if self.quantity >= self.table.large_wholesale_threshold:
            return self.quantity * self.table.large_wholesale_price
        elif self.quantity >= self.table.small_wholesale_threshold:
            return self.quantity * self.table.small_wholesale_price
        return self.quantity * self.table.price

    def __str__(self):
        return f"{self.table.brand} x {self.quantity}"
