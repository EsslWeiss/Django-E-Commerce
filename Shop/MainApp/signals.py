from django.dispatch import receiver
from .models import CartProduct, Cart


def save_cart(sender, instance, **kwargs):
	print('IM HEEEEEREEEE!')
	print('instance: ', instance)
	print('sender: ', sender)
	instance.cart.save()
