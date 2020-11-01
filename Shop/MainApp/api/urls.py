from django.urls import path
from .api_views import (CategoryListAPIView, NotebookListAPIView, 
	SmartphoneListAPIView)


urlpatterns = [
	path('categories/', CategoryListAPIView.as_view()),
	path('notebookproduct/', NotebookListAPIView.as_view()),
	path('smartphoneproduct/', SmartphoneListAPIView.as_view())
]