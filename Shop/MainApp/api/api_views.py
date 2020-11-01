from rest_framework.generics import (
	ListAPIView,  # GET all objects
	RetrieveAPIView,  # GET concreate object
	ListCreateAPIView,  # GET or create (POST) object
	RetrieveUpdateAPIView  # update (PUT) object
) 
from rest_framework.filters import SearchFilter

from .serializers import (CategorySerializer, NotebookProductSerializer, 
	SmartphoneProductSerializer)
from .pagination import CategoryPagination 
from ..models import Category, NotebookProduct, SmartphoneProduct

from collections import OrderedDict


class CategoryListAPIView(ListAPIView):

	serializer_class = CategorySerializer
	pagination_class = CategoryPagination
	queryset = Category.objects.all()


class CategoryCreateUpdateAPIView(ListCreateAPIView, RetrieveUpdateAPIView):

	serializer_class = CategorySerializer
	pagination_class = CategoryPagination
	queryset = Category.objects.all()
	lookup_field = 'id'


class NotebookListAPIView(ListAPIView):

	serializer_class = NotebookProductSerializer
	queryset = NotebookProduct.objects.all()
	filter_backends = (SearchFilter, )
	search_fields = ('price', 'name')

	# def get_queryset(self):
	# 	queryset = super().get_queryset()
	# 	params = self.request.query_params
	# 	filter_params = {
	# 		'price__iexact': params.get('price'),
	# 		'name__iexact': params.get('name')
	# 	}
	# 	return queryset.filter(**filter_params)


class SmartphoneListAPIView(ListAPIView):

	serializer_class = SmartphoneProductSerializer
	queryset = SmartphoneProduct.objects.all()
	filter_backends = (SearchFilter, )
	search_fields = ('price', 'name')
	lookup_field = 'id'


class NotebookDetailAPIView(RetrieveAPIView):

	serializer_class = NotebookProductSerializer
	queryset = NotebookProduct.objects.all()
	filter_backends = (SearchFilter, )
	search_fields = ('price', 'name')
	lookup_field = 'id'


class SmartphoneDetailAPIView(RetrieveAPIView):

	serializer_class = NotebookProductSerializer
	queryset = NotebookProduct.objects.all()
	lookup_field = 'id'
