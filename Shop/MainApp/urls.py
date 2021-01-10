from django.urls import path

from .views import (
 	MainPageView, 
	ProductDetailView, 
 	CategoryDetailView, 
 	CartView, 
 	AddToCartView, 
 	RemoveFromCartView, 
 	AjaxChangeProductQuantityView,
 	MakeOrderView,
# 	MakeOnlinePaymentView
)


urlpatterns = [
    path('', MainPageView.as_view(), name='MainPageView'),
    path('product/<str:slug>/', ProductDetailView.as_view(), 
 		name='ProductDetailView'),
 	path('category/<str:slug>/', CategoryDetailView.as_view(), 
 		name='CategoryDetailView'),
	
 	path('cart/', CartView.as_view(), name='CartView'),
 	path('add-to-cart/<slug:slug>/', AddToCartView.as_view(), 
 		name='AddToCartView'),
 	path('remove-from-cart/<slug:slug>/', RemoveFromCartView.as_view(), 
 		name='RemoveFromCartView'),
	path('change-product-quantity/<slug:slug>/', 
		AjaxChangeProductQuantityView.as_view(), 
 		name='ChangeProductQuantityView'),
	
 	path('checkout/', MakeOrderView.as_view(), name='MakeOrderView'),
# 	path('payed-online-order/', MakeOnlinePaymentView.as_view(), name='MakeOnlinePaymentView'),

]
