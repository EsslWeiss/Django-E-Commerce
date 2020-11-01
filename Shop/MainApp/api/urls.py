from django.urls import path, include
from .api_views import (
	CategoryListAPIView, 
	NotebookListAPIView, 
	SmartphoneListAPIView,
	NotebookDetailAPIView, 
	SmartphoneDetailAPIView)


notebook_patterns = [
	path('', NotebookListAPIView.as_view()),
	path('<str:id>/', NotebookDetailAPIView.as_view()),
]

smartphone_patterns = [
	path('', SmartphoneListAPIView.as_view()),
	path('<str:id>/', SmartphoneDetailAPIView.as_view()),	
]

urlpatterns = [
	path('categories/', CategoryListAPIView.as_view()),
	path('notebookproduct/', include(notebook_patterns)),
	path('smartphoneproduct/', include(smartphone_patterns)),
]