from django import forms
from django.utils.safestring import mark_safe
from PIL import Image

from .models import (
	Product, 
	SmartphoneSpec, 
	NotebookSpec
)


class SmartphoneCategoryChoices(forms.ModelChoiceField): pass


class NotebookCategoryChoices(forms.ModelChoiceField): pass


class ImageValidator:
	"""
	Класс валидации изображения для админ панели
	"""
	RESOLUTION_HELP_TEXT = '\
		<strong style="color: green; font-size: 14px;">Диапазон допустимых разрешений \
        	для загруженых изображений: {}x{} - {}x{}!<strong><br> \
        <strong style="color: red; font-size: 14px">Изображение с разрешением больше \
                	{}x{} будет обрезано до {}x{}!<strong>'
	IMG_SIZE_EXCEED = 'Размер изображения не должен превышать 3MB!'
	IMG_SIZE_BELOW_ACCEPTABLE = 'Разрешение загруженого изображения'\
    	'ниже допустимого значения!'

	@classmethod
	def get_help_text(cls):
		"""
		Метод возвращает RESOLUTION_HELP_TEXT для админ панели в виде Html.
		"""
		safe_help_text = mark_safe(
           	cls.RESOLUTION_HELP_TEXT.format(
            	*Product.MIN_RESOLUTION,
            	*Product.MAX_RESOLUTION * 2,
            	*Product.OPTIMAL_RESOLUTION)
        	)
		return mark_safe(safe_help_text)

	@classmethod
	def validate_image(cls, form):
		"""
		Валидатор изображения для поля image в админ панели.
		form - экземпляр формы.
		"""
		min_height, min_width = Product.MIN_RESOLUTION
		print('FORM!!! ', form)
		image = form.cleaned_data['image']
		img = Image.open(image)  # take image width and height

		if image.size > Product.MAX_IMAGE_SIZE:
			raise forms.ValidationError(
				cls.IMG_SIZE_EXCEED
			)
		
		if img.height < min_height and img.width < min_width:
			raise forms.ValidationError(
				cls.IMG_SIZE_BELOW_ACCEPTABLE
			)

		return image


class SmartphoneValidationForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		instance = kwargs.get('instance') # instance - экземпляр модели Smartphone

		# Если у экземпляра Smartphone нет sd - устанавливаем поле 
		# sd_max_volume в readonly.
		if instance and not instance.sd:
			self.fields['sd_max_volume'].widget.attrs.update({
				'readonly': True,
				'style': 'background: lightgray'
			})

	# def clean_image(self):
	# 	"""
	# 	Проверка поля image на валидность разрешения.
	# 	"""
	# 	validate_image = ImageValidator.validate_image(self)
	# 	return validate_image

	def clean(self):
		if self.cleaned_data['sd'] is False:
			self.cleaned_data['sd_max_volume'] = None

		return self.cleaned_data


class ProductValidationForm(forms.ModelForm):
	"""
	Добавляем RESOLUTION_HELP_TEXT в админ понель для поля image.
	Используем ImageValidator для валидации подя image.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['image'].help_text = ImageValidator.get_help_text()

	def clean_image(self):
		validate_image = ImageValidator.validate_image(self)
		return validate_image
