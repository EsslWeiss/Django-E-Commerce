from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View, DetailView

from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from .models import (NotebookProduct, SmartphoneProduct, Category, 
	AllProducts, Cart, CartProduct, Customer)

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
		self.cart.save()  # Save the cart!
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
			object_id=product.id,
			#full_price=product.price
		)
		cart_product.quantity = int(request.POST.get('quantity'))
		cart_product.save()
		self.cart.save()
		messages.add_message(request, messages.INFO, 'Кол-во товаров в корзине успешно изменено')
		return HttpResponseRedirect('/cart/')
