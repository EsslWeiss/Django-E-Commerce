from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models


class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name='Категория')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(max_length=255, verbose_name='Продукт')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(verbose_name='Изображение')
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.name}- {self.price}$'


class CartProduct(models.Model):

    customer = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина',
                             on_delete=models.CASCADE,
                             related_name='cart_product')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    full_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        return f'{self.product.name}- {self.quantity} quantity'


class Cart(models.Model):

    owner = models.ForeignKey('Customer', verbose_name='Владелец корзины', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Финальная цена')


class Customer(models.Model):

    user = models.ForeignKey(get_user_model(), verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=11, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

