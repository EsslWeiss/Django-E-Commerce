from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .serializers import (CategorySerializer, NotebookProductSerializer, 
	SmartphoneProductSerializer)
from ..models import Category, NotebookProduct, SmartphoneProduct

from collections import OrderedDict


class CategoryPagination(PageNumberPagination):

	page_size = 2
	page_size_query_param = 'page_size'
	max_page_size = 10

	def get_paginated_response(self, data):
		return Response(OrderedDict([
			('objects_count', self.page.paginator.count),
			('next', self.get_next_link()),
			('previous', self.get_previous_link()),
			('items', data),
		]))


class CategoryListAPIView(ListAPIView):

	serializer_class = CategorySerializer
	pagination_class = CategoryPagination
	queryset = Category.objects.all()


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


class NotebookDetailAPIView(RetrieveAPIView):

	serializer_class = NotebookProductSerializer
	queryset = NotebookProduct.objects.all()
	lookup_field = 'id'


class SmartphoneDetailAPIView(RetrieveAPIView):

	serializer_class = NotebookProductSerializer
	queryset = NotebookProduct.objects.all()
	lookup_field = 'id'
