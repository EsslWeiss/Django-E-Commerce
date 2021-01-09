from django.apps import apps
from django.utils.safestring import mark_safe

from .models import NotebookSpec, SmartphoneSpec
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, Count


class SpecProcessing:
	"""
	Класс обработки спецификации для продуктов.
	"""
	TABLE_HEAD = """
			<table class="table">
			<tbody>
	"""
	TABLE_TAIL = """
			</tbody>
			</table>
	"""
	TABLE_CONTENT = """
			<tr>
			    <td>{field}</td>
			    <td>{value}</td>
			</tr>
	"""

	def __init__(self, product=None):
		self.product = product

	def _to_html(self, content, table_head=None, table_tail=None):
		if table_head is None:
			table_head = self.TABLE_HEAD

		if table_tail is None:
			table_tail = self.TABLE_TAIL

		return mark_safe(table_head + content + table_tail)

	@staticmethod
	def _smartphone_spec_proc(spec_dict, spec_model):
		"""
		spec_dict - атрибуты и значения спецификации в виде словаря.
		spec_model - текущая модель спецификации.
		"""
		av = spec_model.sd_available()
		spec_dict[av.sd_field] = av.av_text
		if av.av_bool is False:
			del spec_dict[av.sd_max_volume_field]

		return spec_dict

	def get_spec_in_dict(self, product):
		"""
		product - экземпляр класса Product.
		Получаем по продукту модель его спецификаций.
		Берем спецификацяю, помещаем в словарь.  
		"""
		spec_model = product.content_object  # Берем связанную модель спецификации.
		
		spec = {
			field.verbose_name: getattr(spec_model, field.name)
			for field in spec_model._meta.get_fields()
			if field.name != 'id'
		}  # Получаем словарь вида: {sd.verbose_name: True, diagonal.verbose_name: 'qwerty'}
		if type(spec_model) is SmartphoneSpec:
			spec = self._smartphone_spec_proc(
				spec_dict=spec,
				spec_model=spec_model  # CurrentSpecModel
			)

		return spec

	def get_spec_in_str(self, product):
		spec = self.get_spec_in_dict(product)

		spec_str = ''
		for field_name, field_val in spec.items():
			spec_str += self.TABLE_CONTENT.format(
				field=field_name, value=field_val
			)
		return spec_str

	def get_spec_in_html(self, product):
		spec = self.get_spec_in_str(product)
		return self._to_html(spec)
