from django.urls import path
from .views import WordListView, CreateWordView, DeleteWordView

# URL configuration for Dictionary project.
urlpatterns = [
    path('add_word/', CreateWordView.as_view(), name='add-word'),
    path('words/', WordListView.as_view(), name='word-list'),
    path('delete_word/<uuid:id>/', DeleteWordView.as_view(), name='delete-word')
]
