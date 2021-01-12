import sys

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from .custom_exceptions import MinResolutionErrorException
# from .managers import CategoryManager

from PIL import Image
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone

from collections import ChainMap, namedtuple
import uuid


# class AllProductsManager:

#     @staticmethod
#     def get_products_for_mainpage(*args, **kwargs):
#         sort_priority_model = kwargs.get('sort_priority_model')
#         products = []
#         ct_models = ContentType.objects.filter(model__in=args)

#         for ct_model in ct_models:
#             prod = ct_model.model_class()._base_manager.all().order_by('-id')
#             products.extend(prod)
#         if sort_priority_model:
#             ct_model = ContentType.objects.filter(model=sort_priority_model)
#             if ct_model.exists() and sort_priority_model in args:
#                 return sorted(
#                     products,
#                     key=lambda model: model.__class__._meta.model_name.startswith(sort_priority_model),
#                     reverse=True
#                 )
#         return products


# class AllProducts:

#     objects = AllProductsManager()


class CategoryManager(models.Manager):

    def categories_with_prod_count(self):
        category_prod_count = self.get_queryset().annotate(
            product_count=models.Count('products_related_query')
        )
        return category_prod_count

    def categories_with_prod_count_in_dict(self):
        categories = self.categories_with_prod_count()
        return [
            {
                'name': c.name,
                'url': c.get_absolute_url(),
                'product_count': c.product_count 
            }
            for c in categories
        ]


class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name='Category')
    slug = models.SlugField(unique=True)

    objects = CategoryManager()

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def get_absolute_url(self):
        return reverse('CategoryDetailView', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class Product(models.Model):

    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (800, 800)
    OPTIMAL_RESOLUTION = (800, 600)

    MAX_IMAGE_SIZE = 3145728

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    name = models.CharField(max_length=255, verbose_name='Продукт')
    price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name='Цена')
    
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(verbose_name='Изображение')
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='products_related',
        related_query_name='products_related_query',
        on_delete=models.CASCADE)

    slug = models.SlugField(unique=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('createdAt', 'updatedAt')
        
    def get_absolute_url(self):
        return reverse('ProductDetailView', kwargs={'slug': self.slug})

    def img_resolusion_proc(self):
        """
        Метод обработки разрешения.
        Минимальное значение разрешения: MIN_RESOLUTION
        Изображения, разрешение которых выше MAX_RESOLUTION
        обрезаются до OPTIMAL_RESOLUTION
        """
        curr_image = self.image
        img = Image.open(curr_image)

        min_height, min_width = self.MIN_RESOLUTION
        max_height, max_width = self.MAX_RESOLUTION

        if img.height < min_height and img.width < min_width:
            raise MinResolutionErrorException(
                'Разрешение загруженого изображения ниже допустимого значения!'
            )

        if img.height > max_height and img.width > max_width:
            new_img = img.convert('RGB')
            resized_new_img = new_img.resize(
                self.OPTIMAL_RESOLUTION,
                Image.ANTIALIAS
            )

            filestream = BytesIO()
            resized_new_img.save(filestream, 'JPEG', quality=90)
            filestream.seek(0)
            filename = '{}.{}'.format(*self.image.name.split('.'))
            self.image = InMemoryUploadedFile(
                filestream, 
                'ImageField', 
                filename, 
                'jpeg/image', 
                sys.getsizeof(filestream), 
                None
            )

    def save(self, *args, **kwargs):
        self.img_resolusion_proc()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}- {self.price}$'


class NotebookSpec(models.Model):

    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    display = models.CharField(max_length=255, verbose_name='Дисплей')
    processor = models.CharField(max_length=255, verbose_name='Частота процессора')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    time_without_charge = models.CharField(max_length=255, verbose_name='Время работы аккумулятора')

    def __str__(self):
        return "%s RAM, %s processor" % (self.ram, self.processor)


class SmartphoneSpec(models.Model):

    SD_AVAILABLE_TEXT = 'Есть в наличии'
    SD_NOT_AVAILABLE_TEXT = 'Нет в наличии'
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
    sd_max_volume = models.CharField(
        max_length=255,
        null=True, blank=True,
        choices=CD_MAX_VOLUME_CHOICES,
        verbose_name='Максимальный объем SD карты')
    
    main_camera_mp = models.CharField(max_length=255, verbose_name='Главная камера')
    frontal_camera_mp = models.CharField(
        max_length=255, 
        verbose_name='Фронтальная камера')

    def sd_available(self):
        available = namedtuple('available', [
            'av_bool', 
            'av_text',
            'sd_field',
            'sd_max_volume_field'
        ])
        return available(
            av_bool=self.sd,
            av_text=self.SD_AVAILABLE_TEXT if self.sd else self.SD_NOT_AVAILABLE_TEXT,
            sd_field=self._meta.get_field('sd').verbose_name,
            sd_max_volume_field=self._meta.get_field('sd_max_volume').verbose_name,
        )

    def get_absolute_url(self):
        return self.get_product_url(self, 'ProductDetailView')

    def __str__(self):
        return "%s display - %s diagonal" % (self.display, self.diagonal)


class CartProduct(models.Model):
    """
    Связующая модель между продуктом и корзиной.
    - USE UUID FOR IDENTIFIER CART-PRODUCT IN USER CART!!!
    нужен UUID, чтобы идентифицировать конкретный Cart-Product в Cart покупателя.
    """
    cart_prod_in_cart_id = models.UUIDField(
        default=uuid.uuid4, 
        editable=False,
        unique=True)

    customer = models.ForeignKey(
        'Customer',
        verbose_name='Покупатель',
        on_delete=models.CASCADE,
        related_name='related_cartprod')
    
    cart = models.ForeignKey(
        'Cart',
        verbose_name='Корзина',
        on_delete=models.CASCADE,
        related_name='related_products')  
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='cart_product',
        related_query_name='cart_product_related')
    
    quantity = models.PositiveIntegerField(
        default=1, 
        verbose_name='Количество')
    full_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0,
        verbose_name='Общая цена')

    def save(self, *args, **kwargs):
        self.full_price = self.quantity * self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s - %s quantity' % (
            self.product.name, 
            self.quantity
        )


class Cart(models.Model):

    owner = models.ForeignKey(
        'Customer',
        verbose_name='Владелец корзины',
        related_name='related_cart',
        related_query_name='related_query_cart',
        on_delete=models.CASCADE)

    cart_products = models.ManyToManyField( 
        CartProduct,
        related_name='related_cart')
    
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0,
        verbose_name='Финальная цена')
    
    in_order = models.BooleanField(default=False)

    # True - если пользователь отсутствует в request.user
    for_anonymous_user = models.BooleanField(default=False)

    def update_cart(self):
        cart = self.cart_products.aggregate(
            final_price=models.Sum('full_price'),
            total_products=models.Sum('quantity')
        )
        if cart.get('final_price'):
            self.final_price = cart['final_price'].normalize()
        else:
            self.final_price = 0

        if cart.get('total_products'):
            self.total_products = cart['total_products']
        else:
            self.total_products = 0


    def save(self, *args, **kwargs):
        try:
            self.update_cart()
        except ValueError:
            return super().save(*args, **kwargs)

        return super().save(*args, **kwargs)

    def __str__(self):
        return '%s products for $%s' % (
            self.total_products, self.final_price
        )


class Customer(models.Model):

    user = models.OneToOneField(
        get_user_model(),
        verbose_name='Пользователь',
        on_delete=models.CASCADE)
    
    phone = models.CharField(
        max_length=11,
        null=True,
        verbose_name='Номер телефона')
    address = models.CharField(
        max_length=255,
        null=True,
        verbose_name='Адрес')

    orders = models.ManyToManyField(
        'Order',
        verbose_name='Заказы покупателя',
        blank=True,
        related_name='related_customer')


class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'
    STATUS_PAYED = 'payed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_PAYED, 'Заказ оплачен'),
        (STATUS_NEW, 'новый заказ'),
        (STATUS_IN_PROGRESS, 'заказ в обработке'),
        (STATUS_READY, 'заказ готов'),
        (STATUS_COMPLETED, 'заказ выполнен'),
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'самовывоз'),
        (BUYING_TYPE_DELIVERY, 'доставка')
    )

    customer = models.ForeignKey(
        Customer,
        verbose_name='Покупатель',
        on_delete=models.CASCADE,
        related_name='related_orders')

    cart = models.ForeignKey(
        Cart,
        verbose_name='Корзина',
        blank=True, null=True,
        on_delete=models.CASCADE)
    
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=11, verbose_name='Номер телефона')
    address = models.CharField(
        max_length=1000,
        verbose_name='Адрес доставки',
        blank=True,
        null=True)
    status = models.CharField(
        max_length=70,
        verbose_name='Статус заказа',
        choices=STATUS_CHOICES,
        default=STATUS_NEW)
    buying_type = models.CharField(
        max_length=70,
        verbose_name='Тип заказа',
        choices=BUYING_TYPE_CHOICES,
        default=BUYING_TYPE_SELF)
    comment = models.TextField(
        verbose_name='Комментарий к заказу', 
        blank=True, 
        null=True)
    created_date = models.DateTimeField(
        auto_now=True, 
        verbose_name='Дата создания заказа')
    order_date = models.DateTimeField(
        verbose_name='Дата получения заказа', 
        default=timezone.now)

    class Meta:
        ordering = ('created_date', 'order_date')

    def __str__(self):
        return "%s order with %s status" % (self.buying_type, self.status)
