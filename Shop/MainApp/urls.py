from django.urls import path

from .views import (
	MainPageView, 
	ProductDetailView, 
	CategoryDetailView, 
	CartView, 
	AddToCartView, 
	RemoveFromCartView, 
	ChangeProductQuantityView,
	MakeOrderView
)


urlpatterns = [
    path('', MainPageView.as_view(), name='MainPageView'),
    path('products/<str:ct_model>/<slug:slug>/', ProductDetailView.as_view(), 
		name='ProductDetailView'),
	path('category/<str:slug>', CategoryDetailView.as_view(), 
		name='CategoryDetailView'),
	
	path('cart/', CartView.as_view(), name='CartView'),
	path('add-to-cart/<str:ct_model>/<slug:slug>/', AddToCartView.as_view(), 
		name='AddToCartView'),
	path('remove-from-cart/<str:ct_model>/<slug:slug>/', RemoveFromCartView.as_view(), 
		name='RemoveFromCartView'),
	path('change-product-quantity/<str:ct_model>/<slug:slug>/', ChangeProductQuantityView.as_view(), 
		name='ChangeProductQuantityView'),
	path('checkout/', MakeOrderView.as_view(), name='MakeOrderView'),
]
