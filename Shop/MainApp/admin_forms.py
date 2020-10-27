from django import forms
from PIL import Image
from django.utils.safestring import mark_safe

from .models import Product, SmartphoneProduct


class SmartphoneCategoryChoices(forms.ModelChoiceField): pass


class NotebookCategoryChoices(forms.ModelChoiceField): pass


class ImageValidation:

	@staticmethod
	def get_help_text():
		safe_help_text = mark_safe(
                	'<strong style="color: green; font-size: 14px;">Диапазон допустимых разрешений \
                	для загруженых изображений: {}x{} - {}x{}!<strong><br> \
                	<strong style="color: red; font-size: 14px">Изображение с разрешением больше \
                	{}x{} будет обрезано до {}x{}!<strong>'
                	.format(*Product.MIN_RESOLUTION,
                    	*Product.MAX_RESOLUTION * 2,
                    	*Product.OPTIMAL_RESOLUTION)
                )
		return safe_help_text

	@staticmethod
	def validation_image(form):
		image = form.cleaned_data['image']
		img = Image.open(image)
		min_height, min_width = Product.MIN_RESOLUTION

		if image.size > Product.MAX_IMAGE_SIZE:
			raise forms.ValidationError('Размер изображения не должен превышать 3MB!')
		if img.height < min_height and img.width < min_width:
			raise forms.ValidationError('Разрешение загруженого изображения ниже допустимого значения!')

		return image


class NotebookValidationForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['image'].help_text = ImageValidation.get_help_text()

	def clean_image(self):
		validate_image = ImageValidation.validation_image(self)
		return validate_image


class SmartphoneValidationForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['image'].help_text = ImageValidation.get_help_text()
		instance = kwargs.get('instance')
		if instance and not instance.sd:
			self.fields['sd_max_volume'].widget.attrs.update({
				'readonly': True,
				'style': 'background: lightgray'
			})

	def clean_image(self):
		validate_image = ImageValidation.validation_image(self)
		return validate_image

	def clean(self):
		if not self.cleaned_data['sd']:
			self.cleaned_data['sd_max_volume'] = None

		return self.cleaned_data
