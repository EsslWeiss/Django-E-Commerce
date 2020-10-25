from django import forms
from PIL import Image
from django.utils.safestring import mark_safe

from .models import Product


class SmartphoneCategoryChoices(forms.ModelChoiceField): pass


class NotebookCategoryChoices(forms.ModelChoiceField): pass


class NotebookAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = mark_safe(
                '<strong style="color: green; font-size: 14px;">Диапазон допустимых разрешений \
                для загруженых изображений: {}x{} - {}x{}!<strong><br> \
                <strong style="color: red; font-size: 14px">При загрузке изображения больше \
                {}x{} оно будет обрезано до размера {}x{}!<strong>'
                .format(*Product.MIN_RESOLUTION, 
                    *Product.MAX_RESOLUTION * 2,
                    *Product.OPTIMAL_RESOLUTION)
                )

    def clean_image(self):
        image = self.cleaned_data['image']
        img = Image.open(image)
        min_height, min_width = Product.MIN_RESOLUTION
                
        if image.size > Product.MAX_IMAGE_SIZE:
            raise forms.ValidationError('Размер изображения не должен превышать 3MB!')
        if img.height < min_height and img.width < min_width:
            raise forms.ValidationError('Разрешение загруженого изображения ниже допустимого значения!')

        return image

