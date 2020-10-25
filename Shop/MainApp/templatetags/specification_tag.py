from django import template
from django.utils.safestring import mark_safe

from ..services import SpecificationProcessing


register = template.Library()

@register.filter()
def product_specification(product):	
	product_spec = SpecificationProcessing.get_product_specification(product)
	return product_spec

