from django.urls import path
from .views import MainPageView, ProductDetailView, CategoryDetailView


urlpatterns = [
    path('', MainPageView.as_view(), name='MainPageView'),
    path('products/<str:ct_model>/<slug:slug>/', ProductDetailView.as_view(), 
		name='ProductDetailView'),
	path('category/<str:slug>', CategoryDetailView.as_view(), 
		name='CategoryDetailView'),

]

