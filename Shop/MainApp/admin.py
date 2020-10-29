from django.contrib import admin

from .models import (Category, SmartphoneProduct, NotebookProduct, 
        Cart, CartProduct, Customer, Order)
from .admin_forms import (NotebookCategoryChoices, SmartphoneCategoryChoices, 
	NotebookValidationForm, SmartphoneValidationForm)


class NotebookProductAdmin(admin.ModelAdmin):
    
    form = NotebookValidationForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return NotebookCategoryChoices(Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SmartphoneProductAdmin(admin.ModelAdmin):
	
    form = SmartphoneValidationForm
    change_form_template = 'admin.html'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return SmartphoneCategoryChoices(Category.objects.filter(slug='smartphones'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(SmartphoneProduct, SmartphoneProductAdmin)
admin.site.register(NotebookProduct, NotebookProductAdmin)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Customer)
admin.site.register(Order)
