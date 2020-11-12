import stripe

from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import View, DetailView
from django.db import transaction
from django.conf import settings

from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from .models import (
	NotebookProduct, 
	SmartphoneProduct, 
	Category, 
	AllProducts, 
	Cart, 
	CartProduct, 
	Customer,
	Order
)
from .forms import OrderForm

from .mixins import CategoryDetailMixin, CartMixin
from collections import namedtuple


class MainPageView(CartMixin, View):
	"""
		CartMixin returned Cart object for current user in session. 
	"""

	PRODUCT_MODELS = namedtuple('PRODUCT_MODELS', [
			'notebook', 
			'smartphone',
		])
	PRODUCTS = PRODUCT_MODELS('notebookproduct', 'smartphoneproduct')

	def get(self, request, *args, **kwargs):
		categories = Category.objects.get_categories()
		products = AllProducts.objects.get_products_for_mainpage(
			*self.PRODUCTS, 
			sort_priority_model=self.PRODUCTS.notebook
		)
		context = {
			'categories': categories, 
			'products': products,
			'cart': self.cart
		}

		return render(request, 'index.html', context)


class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):
	"""
		CategoryDetailMixin returned list of 'categories' objects for context.
	"""

	CT_MODEL_CLASSES = {
		'notebookproduct': NotebookProduct,
		'smartphoneproduct': SmartphoneProduct
	}
	
	context_object_name = 'product'
	template_name = 'product_detail.html'
	slug_url_kwarg = 'slug'

	def dispatch(self, request, *args, **kwargs):
		self.model = self.CT_MODEL_CLASSES[kwargs['ct_model']]
		self.queryset = self.model._base_manager.all()
		return super().dispatch(request, *args, **kwargs)
		
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['ct_model'] = self.model._meta.model_name
		context['cart'] = self.cart  # Add cart object to categories page
		return context


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):

	CATEGORY_SLUG_TO_PRODUCT_MODEL = {
		'notebooks': NotebookProduct,
		'smartphones': SmartphoneProduct,
	}

	model = Category 
	queryset = Category.objects.all()
	template_name = 'category_detail.html'
	context_object_name = 'category'
	slug_url_kwarg = 'slug'

	def get_context_data(self, **kwargs):
		# get_object() its Category model.
		context = super().get_context_data(**kwargs)
		product_model = self.CATEGORY_SLUG_TO_PRODUCT_MODEL[self.get_object().slug]
		context['category_products'] = product_model.objects.all()
		context['cart'] = self.cart
		return context


class CartView(CartMixin, View):

	def get(self, request, *args, **kwargs):
		categories = Category.objects.get_categories()
		context = {
			'cart': self.cart,
			'categories': categories
		}
		return render(request, 'cart.html', context)


class AddToCartView(CartMixin, View):

	def get(self, request, *args, **kwargs):
		ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
		content_type_model = ContentType.objects.get(model=ct_model)
		product = content_type_model.model_class().objects.get(slug=product_slug)

		cart_product, created = CartProduct.objects.get_or_create(
			customer=self.cart.owner,
			cart=self.cart,
			content_type=content_type_model,
			object_id=product.id,
			#full_price=product.price
		)
		if created:
			self.cart.products.add(cart_product)
			messages.add_message(request, messages.INFO, 'Товар успешно добавлен')
		
		#recalc_cart_data(self.cart)  # Recalculate data in cart.
		self.cart.save()
		return HttpResponseRedirect('/cart/')


class RemoveFromCartView(CartMixin, View):

	def get(self, request, *args, **kwargs):
		ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
		content_type_model = ContentType.objects.get(model=ct_model)
		product = content_type_model.model_class().objects.get(slug=product_slug)

		cart_product = CartProduct.objects.get(
			customer=self.cart.owner,
			cart=self.cart,
			content_type=content_type_model,
			object_id=product.id,
			#full_price=product.price
		)
		self.cart.products.remove(cart_product)  # deleted! 
		cart_product.delete()
		self.cart.save()
		#recalc_cart_data(self.cart)  # Recalculate data in cart.
		messages.add_message(request, messages.INFO, 'Товар успешно удален')
		return HttpResponseRedirect('/cart/')


class ChangeProductQuantityView(CartMixin, View):

	def post(self, request, *args, **kwargs):
		ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
		content_type_model = ContentType.objects.get(model=ct_model)
		product = content_type_model.model_class().objects.get(slug=product_slug)

		cart_product = CartProduct.objects.get(
			customer=self.cart.owner,
			cart=self.cart,
			content_type=content_type_model,
			object_id=product.id
		)
		cart_product.quantity = int(request.POST.get('quantity'))
		cart_product.save()

		self.cart.total_products = int(request.POST.get('quantity')) 
		#recalc_cart_data(self.cart)  # Recalculate data in cart.
		self.cart.save()

		messages.add_message(request, messages.INFO, 'Кол-во товаров в корзине успешно изменено')
		return HttpResponseRedirect('/cart/')


class MakeOnlinePaymentView(CartMixin, View):

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		customer = Customer.objects.get(user=request.user)

		new_order = Order()
		new_order.customer = customer
		new_order.first_name = customer.user.first_name
		new_order.last_name = customer.user.last_name
		new_order.phone = customer.phone
		new_order.address = customer.address
		new_order.buying_type = self.request.POST.get('buying_type')
		new_order.save()

		self.cart.in_order = True
		new_order.cart = self.cart
		new_order.save()
		self.cart.save()

		customer.orders.add(new_order)  # Add customer a new order.
		return JsonResponse({"status": "payed"})


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
