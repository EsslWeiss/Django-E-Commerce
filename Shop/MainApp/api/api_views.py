from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter

from .serializers import (CategorySerializer, NotebookProductSerializer, 
	SmartphoneProductSerializer)
from ..models import Category, NotebookProduct, SmartphoneProduct


class CategoryListAPIView(ListAPIView):

	serializer_class = CategorySerializer
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
