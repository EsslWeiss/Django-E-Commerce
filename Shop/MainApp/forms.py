from django import forms 
from .models import Order, Customer


class ChangeQuantityForm(forms.Form):

	QUANTITY_ATTRS = {
		'id': 'product_quantity',
		'class': 'form-control',
		'style': 'width: 80px;',
		'onclick': 'take_onclick(event)',
		'min': '1',
		'name': 'quantity'
	}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# self.fields['quantity'].widget.attrs.update({
		# 	'onclick': 'take_onclick(event)'
		# })

	cart_prod_in_cart_id = forms.CharField(widget=forms.HiddenInput)
	quantity = forms.CharField(
		widget=forms.NumberInput(attrs=QUANTITY_ATTRS)
	)

	# class Meta:
	# 	widgets = {
	# 		'quantity': QUANTITY_ATTRS  
	# 	}


class OrderForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['order_date'].label = 'Дата получения заказа'

	order_date = forms.DateField(
		widget=forms.TextInput(attrs={'type': 'date'})
	)

	class Meta:
		model = Order 
		fields = (
			'first_name', 
			'last_name', 
			'phone', 
			'address',
			'buying_type',
			'order_date',
			'comment'
		)


class UserProfileForm(forms.Form):

	username = forms.CharField(
		label='Никнейм', 
		max_length=70,
		required=True)
	first_name = forms.CharField(
		label='Имя', 
		max_length=70, 
		required=False)
	last_name = forms.CharField(
		label='Фамилия', 
		max_length=70,
		required=False)
	email = forms.EmailField(
		label='Электронная почта',
		required=False)
	phone = forms.CharField(
		label='Номер телефона', 
		max_length=12,
		required=False)
	address = forms.CharField(
		label='Адрес', 
		max_length=125, 
		required=False)
