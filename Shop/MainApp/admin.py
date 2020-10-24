from django.contrib import admin

from .models import (Category, SmartphoneProduct, NotebookProduct, 
        Cart, CartProduct, Customer)
from .admin_forms import (NotebookCategoryChoices, SmartphoneCategoryChoices, 
        NotebookAdminForm)


class NotebookProductAdmin(admin.ModelAdmin):
    
    form = NotebookAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return NotebookCategoryChoices(Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SmartphoneProductAdmin(admin.ModelAdmin):

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

