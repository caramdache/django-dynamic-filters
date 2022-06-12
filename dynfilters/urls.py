from django.urls import path, reverse

from . import views

urlpatterns = [
    path('<str:model_name>/add/', views.dynfilters_add, name='dynfilters_add'),
    path('<int:id>/share/', views.dynfilters_share, name='dynfilters_share'),
    path('<int:id>/change/', views.dynfilters_change, name='dynfilters_change'),
    path('<int:id>/delete/', views.dynfilters_delete, name='dynfilters_delete'),
]
