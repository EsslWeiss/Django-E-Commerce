import sys

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from .custom_exceptions import MinResolutionErrorException

from PIL import Image
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile


class AllProductsManager:

    @staticmethod
    def get_products_for_mainpage(*args, **kwargs):
        sort_priority_model = kwargs.get('sort_priority_model')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)

        for ct_model in ct_models:
            prod = ct_model.model_class()._base_manager.all().order_by('-id')
            products.extend(prod)
        if sort_priority_model:
            ct_model = ContentType.objects.filter(model=sort_priority_model)
            if ct_model.exists() and sort_priority_model in args:
                return sorted(
                    products,
                    key=lambda model: model.__class__._meta.model_name.startswith(sort_priority_model),
                    reverse=True
                )
        
        return products


class AllProducts:

    objects = AllProductsManager()


class CategoryManager(models.Manager):

    PRODUCT_MODELS = ('notebookproduct', 'smartphoneproduct')
    CATEGORY_COUNT_NAME = {
        'Ноутбуки': 'notebookproduct__count',
        'Смартфоны': 'smartphoneproduct__count'
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories(self):
        product_count = list(self.get_queryset()
            .annotate(
                *(lambda *model_name: [models.Count(name) for name in model_name])
                (*self.PRODUCT_MODELS)
            )
        )

        return [
            {
                'name': category.name,
                'url': category.get_absolute_url(),
                'count': getattr(category, self.CATEGORY_COUNT_NAME[category.name])
            } for category in product_count
        ]


class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name='Категория')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def get_absolute_url(self): 
        return reverse('CategoryDetailView', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class Product(models.Model):

    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (800, 800)
    OPTIMAL_RESOLUTION = (800, 600)

    MAX_IMAGE_SIZE = 3145728

    name = models.CharField(max_length=255, verbose_name='Продукт')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(verbose_name='Изображение')
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)

    class Meta:
        abstract = True

    @staticmethod
    def get_product_url(product_obj, viewname):
        ct_model = product_obj.__class__._meta.model_name  # get model name in lowercase
        return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': product_obj.slug})

    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)

        min_height, min_width = self.MIN_RESOLUTION
        max_height, max_width = self.MAX_RESOLUTION

        if img.height < min_height and img.width < min_width:
            raise MinResolutionErrorException('Разрешение загруженого изображения ниже допустимого значения!')
        if img.height > max_height and img.width > max_width:
            new_img = img.convert('RGB')
            resized_new_img = new_img.resize(self.OPTIMAL_RESOLUTION, Image.ANTIALIAS)

            filestream = BytesIO()
            resized_new_img.save(filestream, 'JPEG', quality=90)
            filestream.seek(0)

            filename = '{}.{}'.format(*self.image.name.split('.'))
            self.image = InMemoryUploadedFile(
                filestream, 'ImageField', filename, 'jpeg/image', sys.getsizeof(filestream), None
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}- {self.price}$'


class NotebookProduct(Product):

    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    display = models.CharField(max_length=255, verbose_name='Дисплей')
    processor = models.CharField(max_length=255, verbose_name='Частота процессора')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    time_without_charge = models.CharField(max_length=255, verbose_name='Время работы аккумулятора')

    image = models.ImageField(verbose_name='Изображение ноутбука', upload_to='notebooks/')

    def get_absolute_url(self):
        return self.get_product_url(self, 'ProductDetailView')

    def __str__(self):
        return f'{self.category.name}- {self.name}'


class SmartphoneProduct(Product):

    CD_MAX_VOLUME_CHOICES = (
        ("2", "2 GB"),
        ("4", "4 GB"),
        ("6", "6 GB"),
        ("8", "8 GB"),
        ("16", "16 GB"),
    )

    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    display = models.CharField(max_length=255, verbose_name='Дисплей')
    resolution = models.CharField(max_length=255, verbose_name='Разрешение экрана')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    sd = models.BooleanField(default=True, verbose_name='Наличие SD карты')
    sd_max_volume = models.CharField(max_length=255, null=True, blank=True,
        choices=CD_MAX_VOLUME_CHOICES,
        verbose_name='Максимальный объем SD карты')
    main_camera_mp = models.CharField(max_length=255, verbose_name='Главная камера')
    frontal_camera_mp = models.CharField(max_length=255, verbose_name='Фронтальная камера')
    image = models.ImageField(verbose_name='Изображение смартфона', upload_to='smartphones/')

    def sd_available(self):
    	if not self.sd:
    		return 'Нет в наличии'
    	return 'Есть в наличии'

    def get_absolute_url(self):
        return self.get_product_url(self, 'ProductDetailView')

    def __str__(self):
        return f'{self.category.name}- {self.name}'


class CartProduct(models.Model):

    customer = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина',
                             on_delete=models.CASCADE,
                             related_name='related_products')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    full_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        return f'{self.content_object.name}- {self.quantity} quantity'


class Cart(models.Model):

    owner = models.ForeignKey('Customer', verbose_name='Владелец корзины', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Финальная цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)


class Customer(models.Model):

    user = models.ForeignKey(get_user_model(), verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=11, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
