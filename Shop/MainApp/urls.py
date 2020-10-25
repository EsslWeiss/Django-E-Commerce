from django.urls import path
from .views import index, ProductDetailView


urlpatterns = [
    path('', index, name='main_page'),
    path('products/<str:ct_model>/<slug:slug>/', ProductDetailView.as_view(), 
	name='product_detail'),
]

