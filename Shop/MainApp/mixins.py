from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from django.contrib.auth.models import User

from .models import (
	Category, 
	Cart, 
	Customer
)
from .custom_exceptions import NeedCustomerException

from datetime import datetime
from random import randint


class CategoryDetailMixin(SingleObjectMixin):
	"""
	Миксин, добавляющий категории к контексту
	Пример добавляемых категорий: [
		{'name': cat_name, 'url': cat_url, product_count: prod_in_curr_cat}
	]
	"""
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['categories'] = Category.objects.get_categories()
		return context


class CartMixin:
	"""
	Миксин добавляет объект корзины для текущего пользователя в request.user
	Для пользователя в request.user нет профиля в Customer - создаём новый.
	Если пользователя нет в request.user - отдаём или создаём корзину для 
	анонимных пользователей.
	"""
	@staticmethod
	def _get_or_create_auth_user(request):
		"""
		request - экземпляр HttpRequest
		Функция проверки наличия профиля покупателя для пользователя в request.user. 
		Если пользователь аутентифицирован - пытаемся получить его профиль покупателя,
		Иначе создаём новый.
		Если пользователь не аутентифицирован возвращаем нового пользователя.
		"""
		if request.user.is_authenticated:
			customer, created = Customer.objects.get_or_create(
				user=request.user
			)
		else:
			usrname = 'anon%s' % (random.randit(1, 1_000_000))
			d = datetime.now().day
			h = datetime.now().hour
			s = datetime.now().second
			pswrd = "anonymous%spasswrd%s" % (
				str(d) + str(h) + str(s),
				d + h + s
			)
			anon_user = User.objects.create(
				username=usrname,
				password=pswrd
			)
			customer = Customer.objects.create(user=anon_user)

		return customer

	@staticmethod
	def _get_or_create_cart(customer):
		cart, created = Cart.objects.get_or_create(owner=customer)
		return cart

	def get_cart(self, request):
		"""
		Функция возвращает корзину пользователя.
		"""
		customer = self._get_or_create_auth_user(request)
		cart = self._get_or_create_cart(customer)
		cart.save()
		return cart

	def get_cart_with_customer(self, request):
		"""
		Функция возвращает корзину вместе с её владельцем.
		"""
		customer = self._get_or_create_auth_user(request)
		cart = self._get_or_create_cart(customer)
		cart.save()
		return (customer, cart)


class ProductManageMixin:

	def pack_products(self, cart_prod):
		return [
			{
				'cart_prod_in_cart_id': cp.cart_prod_in_cart_id,
				'name': cp.product.name,
				'price': cp.product.price,
				'slug': cp.product.slug,
				'image': cp.product.image,
				'quantity': cp.quantity,
				'full_price': cp.full_price
			}
			for cp in cart_prod
		]
