from django.contrib import admin

from .models import (
    Category, 
    Product,
    SmartphoneSpec, 
    NotebookSpec, 
    Cart, 
    CartProduct, 
    Customer, 
    Order)
from .admin_forms import (
	ProductValidationForm,
    NotebookCategoryChoices, 
    SmartphoneCategoryChoices, 
    SmartphoneValidationForm)


@admin.register(SmartphoneSpec)
class SmartphoneSpecAdmin(admin.ModelAdmin):
	
    form = SmartphoneValidationForm
    change_form_template = 'admin.html'

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'category':
    #         return SmartphoneCategoryChoices(
    #         	Category.objects.filter(slug='smartphones')
    #         )
        
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

	form = ProductValidationForm
	prepopulated_fields = {"slug": ("name", )}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	
	prepopulated_fields = {'slug': ('name', )}


admin.site.register(NotebookSpec)

admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Customer)
admin.site.register(Order)
