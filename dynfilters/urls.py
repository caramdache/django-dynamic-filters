from django.urls import path

from .views import dynfilters_share

urlpatterns = [
    path('<int:id>/share/', dynfilters_share, name='dynfilters_share'),
]
