from django.apps import AppConfig

from django.db.models.signals import post_delete, post_save
from .signals import save_cart
from .models import CartProduct


class MainappConfig(AppConfig):
    name = 'MainApp'

    def ready(self):
    	post_delete.connect(save_cart, sender=CartProduct)
    	post_save.connect(save_cart, sender=CartProduct)
   