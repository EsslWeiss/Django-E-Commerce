from django.shortcuts import render
from django.views.generic import View, DetailView

from .models import (NotebookProduct, SmartphoneProduct, Category, 
	AllProducts, Cart, Customer)
from .mixins import CategoryDetailMixin

from collections import namedtuple


class MainPageView(View):

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
			'products': products
		}

		return render(request, 'index.html', context)


class ProductDetailView(CategoryDetailMixin, DetailView):

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
		

class CategoryDetailView(CategoryDetailMixin, DetailView):

	model = Category 
	queryset = Category.objects.all()
	template_name = 'category_detail.html'
	context_object_name = 'category'
	slug_url_kwarg = 'slug'


class CartView(View):

	def get(self, request, *args, **kwargs):
		customer = Customer.objects.get(user=request.user)
		cart = Cart.objects.get(owner=customer)
		categories = Category.objects.get_categories()
		context = {
			'cart': cart,
			'categories': categories
		}
		return render(request, 'cart.html', context)

