from django.utils.safestring import mark_safe


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
			'Встраиваемая память': 'sd',
			'Максимальный объем встраиваемой памяти': 'sd_max_volume',
			'Главная камера': 'main_camera_mp',
			'Фронтальная камера': 'frontal_camera_mp'
		}
	}

	@classmethod
	def _mark_safing(cls, content):
		return mark_safe(cls.TABLE_HEAD + content + cls.TABLE_TAIL)

	@classmethod
	def _smartphone_spec_processing(cls, product):
		sd_availability = False
		content = ''
		for name, value in cls.SPECIFICATION['smartphoneproduct'].items():
			if value is 'sd' and getattr(product, value) is sd_availability:
				content += cls.TABLE_CONTENT.format(name=name, value='Нет в наличии')
				continue
			elif value is 'sd':
				content += cls.TABLE_CONTENT.format(name=name, value='Есть в наличии')
				sd_availability = True
				continue
			if value is 'sd_max_volume' and sd_availability is False:
				continue
			content += cls.TABLE_CONTENT.format(name=name, value=getattr(product, value))	
		return content

	@classmethod
	def get_product_specification(cls, product):
		content = ''
		model_name = product.__class__._meta.model_name
		if not (model_name == 'smartphoneproduct'):
			for name, value in cls.SPECIFICATION[model_name].items():
				content += cls.TABLE_CONTENT.format(name=name, value=getattr(product, value))
		else:
			content = cls._smartphone_spec_processing(product)
		
		safing_content = cls._mark_safing(content)
		return safing_content

