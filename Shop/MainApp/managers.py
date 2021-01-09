from django.db.models import Manager, Count
from MainApp.models import Product, Category
from django.contrib.contenttypes.models import ContentType


class CategoryManager(Manager):
    # reformat = [for i in self.CATEGORY_COUNT_NAME]
    def get_categories(self):
        PRODUCT_MODELS_NAME = [
            ct.model_class().__name__.lower()
            for ct in ContentType.objects.all()
            if issubclass(ct.model_class(), Product)
        ]
        # CATEGORY_COUNT_NAME = [
        #     c['name']: 'notebookproduct__count',
        #     for c in Category.objects.values('name')
        # ]
        category_prod_count = list(
            self.get_queryset().annotate(
                count=*(lambda models_name: [
                    models.Count(name) for name in models_name
                    ])(self.PRODUCT_MODELS_NAME)
            )
        )
        return [
            {
                'name': c.name,
                'url': c.get_absolute_url(),
                'count': c.count
            }
            for c in category_prod_count
        ]
