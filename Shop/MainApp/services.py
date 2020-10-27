from django.utils.safestring import mark_safe
from .models import SmartphoneProduct, NotebookProduct


class SpecificationProcessing:

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
			      <td>{name}</td>
			      <td>{value}</td>
			    </tr>
	"""

	SPECIFICATION = {
		'notebookproduct': {
			'Диагональ': 'diagonal',
			'Дисплей': 'display',
			'Процессор': 'processor',
			'Оперативная память': 'ram',
			'Время работы аккумулятора': 'time_without_charge'
		},
		'smartphoneproduct': {
			'Диагональ': 'diagonal',
			'Дисплей': 'display',
			'Разрешение экрана': 'resolution',
			'Оперативная память': 'ram',
			'Наличие SD карты': 'sd',
			'Максимальный объем SD карты': 'sd_max_volume',
			'Главная камера': 'main_camera_mp',
			'Фронтальная камера': 'frontal_camera_mp'
		}
	}

	@staticmethod
	def _to_html(content, table_head, table_tail):
		return mark_safe(table_head + content + table_tail)

	@classmethod
	def _smartphone_spec(cls, product, model_name):
		content = ''

		for name, value in cls.SPECIFICATION[model_name].items():
			if value is 'sd':
				content += cls.TABLE_CONTENT.format(name=name, value=product.sd_available())
				continue

			content += cls.TABLE_CONTENT.format(name=name, value=getattr(product, value))

		return content

	@classmethod
	def _notebook_spec(cls, product, model_name):
		content = ''

		for name, value in cls.SPECIFICATION[model_name].items():
			content += cls.TABLE_CONTENT.format(name=name, value=getattr(product, value))

		return content

	@classmethod
	def get_product_specification(cls, product):
		model_name = product.__class__._meta.model_name

		if isinstance(product, SmartphoneProduct):
			if not product.sd:
				cls.SPECIFICATION[model_name].pop('Максимальный объем SD карты')

			content = cls._smartphone_spec(product, model_name)
		elif isinstance(product, NotebookProduct):
			content = cls._notebook_spec(product, model_name)

		html_content = cls._to_html(content, cls.TABLE_HEAD, cls.TABLE_TAIL)
		return html_content
