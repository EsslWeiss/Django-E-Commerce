# from rest_framework import serializers
# from ..models import Category, SmartphoneProduct, NotebookProduct


# class CategorySerializer(serializers.ModelSerializer):

# 	name = serializers.CharField(required=True)
# 	slug = serializers.SlugField()

# 	class Meta:
# 		model = Category
# 		fields = ('id', 'name', 'slug')


# class BaseProductSerializer:
# 	"""
# 		Serialize base product fields
# 	"""
# 	category = serializers.PrimaryKeyRelatedField(queryset=Category.objects)
# 	name = serializers.CharField(required=True)
# 	price = serializers.DecimalField(max_digits=9, decimal_places=2, required=True)
# 	description = serializers.CharField(required=True)
# 	image = serializers.ImageField(required=True)
# 	slug = serializers.SlugField(required=True)


# class NotebookProductSerializer(BaseProductSerializer, serializers.ModelSerializer):
# 	"""
# 		Serialize notebook product fields 
# 	"""
# 	category = CategorySerializer()

# 	diagonal = serializers.CharField(required=True)
# 	display = serializers.CharField(required=True)
# 	processor = serializers.CharField(required=True)
# 	ram = serializers.CharField(required=True)
# 	time_without_charge = serializers.CharField(required=True)
# 	image = serializers.ImageField(required=True)


# 	class Meta:
# 		model = NotebookProduct
# 		fields = '__all__'


# class SmartphoneProductSerializer(BaseProductSerializer, serializers.ModelSerializer):
# 	"""
# 		Serialize notebook product fields 
# 	"""
# 	CD_MAX_VOLUME_CHOICES = (
#         ("2", "2 GB"),
#         ("4", "4 GB"),
#         ("6", "6 GB"),
#         ("8", "8 GB"),
#         ("16", "16 GB"),
#     )

# 	category = CategorySerializer()

# 	diagonal = serializers.CharField(required=True)
# 	display = serializers.CharField(required=True)
# 	resolution = serializers.CharField(required=True)
# 	ram = serializers.CharField(required=True)
# 	sd = serializers.BooleanField(required=True)
# 	sd_max_volume = serializers.ChoiceField(
#         choices=CD_MAX_VOLUME_CHOICES,
#         required=True)
# 	main_camera_mp = serializers.CharField(required=True)
# 	frontal_camera_mp = serializers.CharField(required=True)
# 	image = serializers.ImageField(required=True)

# 	class Meta:
# 		model = SmartphoneProduct
# 		fields = '__all__'
