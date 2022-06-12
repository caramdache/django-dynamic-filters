from furl import furl

from django import forms
from django.apps import apps
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from .models import (
    DynamicFilterExpr,
    DynamicFilterTerm,
    DynamicFilterColumn,
    DynamicFilterColumnSortOrder,
)

from .forms import (
    DynamicFilterExprForm,
    DynamicFilterTermInlineForm,
    DynamicFilterTermInlineFormSet,
)

from .model_helpers import (
    get_model_admin,
    get_model_choices,
    get_dynfilters_fields,
)

from .url_helpers import redirect_to_referer_next


class DynamicFilterInline(admin.TabularInline):
    extra = 0

    def formfield_for_dbfield(self, db_field, **kwargs):
        obj = kwargs['request'].parent_object

        if db_field.name == 'field' and obj:
            model_admin = get_model_admin(obj)
            kwargs['widget'] = forms.Select(choices=get_dynfilters_fields(model_admin))

        return super().formfield_for_dbfield(db_field, **kwargs)

class DynamicFilterTermInline(SortableInlineAdminMixin, DynamicFilterInline):
    model = DynamicFilterTerm
    form = DynamicFilterTermInlineForm
    formset = DynamicFilterTermInlineFormSet
    verbose_name = 'Search Criteria'
    verbose_name_plural = 'Search Criterias'


class DynamicFilterColumnInline(SortableInlineAdminMixin, DynamicFilterInline):
    model = DynamicFilterColumn
    verbose_name = 'Display Column'
    verbose_name_plural = 'Display Columns'


class DynamicFilterColumnSortOrderInline(SortableInlineAdminMixin, DynamicFilterInline):
    model = DynamicFilterColumnSortOrder
    verbose_name = 'Sort Order'
    verbose_name_plural = 'Sort Orders'


@admin.register(DynamicFilterExpr)
class DynamicFilterExprAdmin(SortableAdminBase, admin.ModelAdmin):
    form = DynamicFilterExprForm
    inlines = [DynamicFilterTermInline]#, DynamicFilterColumnInline, DynamicFilterColumnSortOrderInline]

    list_per_page = 50
    list_display = ('_name', 'model', '_creator')

    def get_form(self, request, obj=None, **kwargs):
        request.parent_object = obj
        return super().get_form(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'model':
            kwargs['widget'] = forms.Select(choices=get_model_choices())

        if db_field.name == 'user':
            db_field.default = kwargs['request'].user

        return super().formfield_for_dbfield(db_field,**kwargs)

    def response_add(self, request, obj, post_url_continue=None):
        response = super().response_add(request, obj, post_url_continue)
        
        return redirect_to_referer_next(request, response)

    def response_change(self, request, obj):
        response = super().response_change(request, obj)

        return redirect_to_referer_next(request, response)

    def _creator(self, obj):
        return obj.user

    def _name(self, obj):
        href = reverse('admin:dynfilters_dynamicfilterexpr_change', args=(obj.id,))
        
        return format_html(f'<a href="{href}">{obj.name}</a>')
