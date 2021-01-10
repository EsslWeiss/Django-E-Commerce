#import stripe

from django.urls import reverse
from django.shortcuts import render
from django.http import (
	Http404, 
	HttpResponseRedirect, 
	JsonResponse
)
from django.views.generic import View, DetailView
from django.db import transaction
from django.db.models import Count, Max
from django.contrib.contenttypes.models import ContentType

from django.conf import settings
from django.contrib import messages
from .models import (
	Product,
	NotebookSpec, 
	SmartphoneSpec, 
	Category, 
	#AllProducts, 
	Cart, 
	CartProduct, 
	Customer,
	Order
)
from .forms import OrderForm, ChangeQuantityForm
from .mixins import CategoryDetailMixin, CartMixin, ProductManageMixin


class MainPageView(CartMixin, View):
	"""
		- CartMixin возвращает корзину для текущего пользователя в request.user
	"""

	def get(self, request, *args, **kwargs):
		"""
		Возвращаем категории, продукты и корзину пользователя на главную страницу.
		"""
		# Категории имеют поле product_count с количеством продуктов в категории.
		categories = Category.objects.categories_with_prod_count_in_dict()
		products = Product.objects.all()
		cart = self.get_cart(request)
		context = {
			'categories': categories, 
			'products': products,
			'total_products': cart.total_products
		}
		return render(request, 'index.html', context)


class ProductDetailView(CartMixin, DetailView):
	"""
	Представление вовзвращает детальную информацию о продукте.
	"""
	model = Product
	queryset = Product.objects.all()
	context_object_name = 'product'
	template_name = 'product_detail.html'
	slug_url_kwarg = 'slug'

	def get_object(self, queryset=None):
		"""
		- Берем слаг из GET-параметра.
		- Получаем конкретный продукт по слагу.
		пример: ProductQueryset
		"""
		if not queryset:
			queryset = self.get_queryset()

		product_slug = self.kwargs.get(self.slug_url_kwarg)
		try:
			current_prod = queryset.get(slug=product_slug)
		except self.model.DoesNotExist:
			raise Http404('%(verbose_name) not found...' % {
					'verbose_name': queryset.model._meta.verbose_name
				}
			)
		return current_prod

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		cart = self.get_cart(self.request)

		context['product'] = self.get_object()
		# context['cart'] = cart
		context['categories'] = Category.objects.categories_with_prod_count_in_dict()
		context['total_products'] = cart.total_products
		return context


class CategoryDetailView(CartMixin, DetailView):
	"""
	Представление возвращает продукты, связанные с конкретной категорией.
	"""
	model = Category
	queryset = Category.objects.all()
	template_name = 'category_detail.html'
	slug_url_kwarg = 'slug'

	def get_object(self, queryset=None):
		"""
		- Получаем слаг категории из GET-параметров.
		- Получаем конкретную категорию по слагу.
		- Получаем связанные с категорией продукты.
		Возвращаемое значение: tuple('current_category', ProductQueryset)
		"""
		if not queryset:
			queryset = self.get_queryset()

		category_slug = self.kwargs.get(self.slug_url_kwarg)
		try:
			current_cat = queryset.get(slug=category_slug)
		except self.model.DoesNotExist:
			raise Http404('%(verbose_name) not found...' % {
					'verbose_name': queryset.model._meta.verbose_name
				}
			)		
		return (
				current_cat,
				current_cat.products_related.all()
			)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		cart = self.get_cart(self.request)
		categories = Category.objects.categories_with_prod_count()
		current_cat, cat_products = self.get_object(categories)

		context['current_category'] = current_cat
		context['category_products'] = cat_products
		context['total_products'] = cart.total_products
		context['categories'] = categories
		
		return context


class CartView(CartMixin, ProductManageMixin, View):
	"""
	Представление возвращает шаблон корзины.
	"""
	def get(self, request, *args, **kwargs):
		cart = self.get_cart(request)
		categories = Category.objects.categories_with_prod_count_in_dict()		
		
		cart_prod = cart.cart_products.all()
		products = self.pack_products(cart_prod)

		context = {
			'total_products': cart.total_products,
			'final_price': cart.final_price,
			'categories': categories,
			'products': products,
			'products_count': cart_prod.count,
		}

		return render(request, 'cart.html', context)


class AddToCartView(CartMixin, View):
	"""
	Представление добавления товара в корзину пользователя.
	Возможно добавление одного товара в корзину из каталога.
	Если товар ранее не был добавлен в корзину - добавляем его в корзину и
	редиректим пользователя на страницу корзины.
	"""
	SUCCESS_ADD = 'Товар успешно добавлен в корзину'

	def get(self, request, *args, **kwargs):
		customer, cart = self.get_cart_with_customer(request)
		product_slug = kwargs.get('slug')
		product = Product.objects.get(slug=product_slug)

		cart_product, created = CartProduct.objects.get_or_create(
			customer=customer,
			cart=cart,
			product=product
		)
		if created:
			cart.cart_products.add(cart_product)  # Добавляем CartProduct в корзину
			messages.add_message(request, messages.INFO, self.SUCCESS_ADD)

		cart.save()
		return HttpResponseRedirect('/cart/')


class RemoveFromCartView(CartMixin, ProductManageMixin, View):
	"""
	Представление удаления товара из корзины.
	"""
	def post(self, request, *args, **kwargs):
		if not request.POST.get('cart_prod_in_cart_id'):
			raise Http404('Что-то пошло не так...')

		cp_in_cart_id = request.POST.get('cart_prod_in_cart_id')

		product_slug = kwargs.get('slug')
		product = Product.objects.get(slug=product_slug)

		customer, cart = self.get_cart_with_customer(request)
		cart_product = CartProduct.objects.get(
			cart_prod_in_cart_id=cp_in_cart_id,
			customer=customer,
			cart=cart
		)		
		cart.cart_products.remove(cart_product)  # Удаляем CartProduct из корзины.
		cart_product.delete()  # Удаляем CartProduct
		cart.save()

		# categories = Category.objects.categories_with_prod_count_in_dict()
		# cart_prod = cart.cart_products.all()
		# products = self.pack_products(cart_prod)  # Use ProductManageMixin.
		# context = {
		# 	'categories': categories,
		# 	'products': products,
		# 	'products_count': cart_prod.count(),
		# }
		# print(context)

		return JsonResponse({'redirect_url': reverse('CartView')})
		# return HttpResponseRedirect('/cart/')


	# def get(self, request, *args, **kwargs):
	# 	customer, cart = self.get_cart_with_customer(request)
	# 	product_slug = kwargs.get('slug')
	# 	product = Product.objects.get(slug=product_slug)
	# 	# categories = Category.objects.categories_with_prod_count()

	# 	cart_product = CartProduct.objects.get(
	# 		customer=customer,
	# 		cart=cart,
	# 	)
	# 	cart.cart_products.remove(cart_product)  # Удаляем CartProduct из корзины.
	# 	cart_product.delete()  # Удаляем CartProduct
	# 	cart.save()

	# 	# cart_prod = cart.cart_products.all()
	# 	# products = self.pack_products(cart_prod)
	# 	# context = {
	# 	# 	'cart': cart,
	# 	# 	'categories': categories,
	# 	# 	'products': products,
	# 	# 	'products_count': cart_prod.count,
	# 	# }
	# 	# messages.add_message(request, messages.INFO, self.ACCESS_DELETE)
	# 	# return JsonResponse({'redirect': reverse('CartView')})
	# 	return HttpResponseRedirect('/cart/')


class AjaxChangeProductQuantityView(CartMixin, View):
	"""
	Изменение кол-ва продуктов в корзине.
	"""
	def update_product(self, cart, cart_prod):
		total_products = cart.total_products
		final_price = cart.final_price
		return {
				'quantity': cart_prod.quantity,
				'full_price': cart_prod.full_price,
				'total_products': total_products,
				'final_price': final_price,
			}

	def post(self, request, *args, **kwargs):
		p = request.POST
		if (p.get('quantity') and int(p.get('quantity')) < 0)\
			or not p.get('cart_prod_in_cart_id'):
			return Http404('Что-то пошло не так...')

		customer, cart = self.get_cart_with_customer(request)
		product_slug = kwargs.get('slug')
		product = Product.objects.get(slug=product_slug)
		cp = CartProduct.objects.get(
			customer=customer,
			cart_prod_in_cart_id=p.get('cart_prod_in_cart_id')
		)

		new_quantity = int(p.get('quantity'))
		cp.quantity = new_quantity
		cp.save()  # При сохранении обновляется поле full_price.

		cart.total_products = (cart.total_products + new_quantity)
		cart.save()  # При сохранении обновляются поля final_price и total_products.

		context = self.update_product(cart, cp)
		return JsonResponse(context)


# class MakeOnlinePaymentView(CartMixin, View):

# 	@transaction.atomic
# 	def post(self, request, *args, **kwargs):
# 		customer = Customer.objects.get(user=request.user)

# 		new_order = Order()
# 		new_order.customer = customer
# 		new_order.first_name = customer.user.first_name
# 		new_order.last_name = customer.user.last_name
# 		new_order.phone = customer.phone
# 		new_order.address = customer.address
# 		new_order.buying_type = self.request.POST.get('buying_type')
# 		new_order.save()

# 		self.cart.in_order = True
# 		new_order.cart = self.cart
# 		new_order.save()
# 		self.cart.save()

# 		customer.orders.add(new_order)  # Add customer a new order.
# 		return JsonResponse({"status": "payed"})


class MakeOrderView(CartMixin, View):

	def get(self, request, *args, **kwargs):
		stripe.api_key = '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'

		payment_intent = stripe.PaymentIntent.create(
		  amount=int(self.cart.final_price * 100),
		  currency='usd',
		  metadata={'integration_check': 'accept_a_payment'}
		)

		form = OrderForm(request.POST or None)
		categories = Category.objects.get_categories()
		context = {
			'cart': self.cart,
			'categories': categories,
			'form': form, 
			'client_secret': payment_intent.client_secret
		}
		return render(request, 'checkout.html', context)

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		form = OrderForm(request.POST or None)
		customer = Customer.objects.get(user=request.user)
		if form.is_valid():
			new_order = form.save(commit=False)
			new_order.customer = customer
			new_order.first_name = form.cleaned_data['first_name']
			new_order.last_name = form.cleaned_data['last_name']
			new_order.phone = form.cleaned_data['phone']
			new_order.address = form.cleaned_data['address']
			new_order.buying_type = form.cleaned_data['buying_type']
			new_order.order_date = form.cleaned_data['order_date']
			new_order.comment = form.cleaned_data['comment']
			new_order.save()

			self.cart.in_order = True
			new_order.cart = self.cart
			new_order.save()
			self.cart.save()

			customer.orders.add(new_order)  # Add customer a new order.
			messages.add_message(request, messages.INFO, 'Благодарим вас за заказ! Менеджер свяжется с вами в течении дня.')			
			return HttpResponseRedirect('/')
		return HttpResponseRedirect('/checkout/')
