from django import template
from django.utils.safestring import mark_safe

from ..services import SpecProcessing


register = template.Library()

@register.filter()
def product_specification(product):
	"""
	Шаблонный тэг возвращает спецификацию продуктов.
	"""
	spec_proc = SpecProcessing()
	return spec_proc.get_spec_in_html(product)
