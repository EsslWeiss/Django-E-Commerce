from django.urls import path, include
from .api_views import (
	CategoryListAPIView,
	CategoryCreateUpdateAPIView, 
	NotebookListAPIView, 
	SmartphoneListAPIView,
	NotebookDetailAPIView, 
	SmartphoneDetailAPIView
)


notebook_patterns = [
	path('', NotebookListAPIView.as_view()),
	path('<str:id>/', NotebookDetailAPIView.as_view()),
]

smartphone_patterns = [
	path('', SmartphoneListAPIView.as_view()),
	path('<str:id>/', SmartphoneDetailAPIView.as_view()),	
]

category_patterns = [
	path('', CategoryListAPIView.as_view()),
	path('<str:id>/', CategoryCreateUpdateAPIView.as_view()),
]

urlpatterns = [
	path('categories/', include(category_patterns)),
	path('notebookproduct/', include(notebook_patterns)),
	path('smartphoneproduct/', include(smartphone_patterns)),
]