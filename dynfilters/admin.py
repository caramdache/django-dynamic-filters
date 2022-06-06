from furl import furl
from operator import itemgetter

from django import forms
from django.apps import apps
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.shortcuts import redirect
from django.utils.html import format_html, format_html_join

from adminsortable2.admin import SortableAdminBase, SortableAdminMixin, SortableInlineAdminMixin, CustomInlineFormSet

from .models import (
    DynamicFilterExpr,
    DynamicFilterTerm,
    DynamicFilterColumn,
    DynamicFilterColumnSortOrder,
)

from .utils import (
    get_model_admin,
    get_model_name, 
    get_qualified_model_name,
    has_dynfilter,
    str_as_date, 
    str_as_date_range,
)


def get_field_choices(obj):
    model_admin = get_model_admin(obj)
    return getattr(model_admin, 'dynfilters_fields', [])

class DynamicFilterInline(admin.TabularInline):
    extra = 0

    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs['request']
        obj = request.parent_object

        if db_field.name == 'field' and obj:
            kwargs['widget'] = forms.Select(choices=get_field_choices(obj))

        return super().formfield_for_dbfield(db_field,**kwargs)


class DynamicFilterTermInlineFormSet(CustomInlineFormSet):
    pass


class DynamicFilterTermInlineForm(forms.ModelForm):
    class Meta:
        model = DynamicFilterTerm
        fields = ('op', 'field', 'lookup', 'value', 'bilateral', 'order')

    def clean(self):
        errors = {}

        op, field, lookup, value = itemgetter('op', 'field', 'lookup', 'value')(self.cleaned_data)

        if op in ('-', '!'):
            if field == '-':
                errors.update({'field': 'Missing value'})

            if lookup == '-':
                errors.update({'lookup': 'Missing value'})

            if not value:
                if lookup in ('-', 'iexact', 'icontains', 'range', 'lt', 'gt', 'lte', 'gte'):
                    errors.update({'value': 'Missing value'})

            else:
                if 'date' in field:
                    if lookup == 'range':
                        try:
                            str_as_date_range(value)
                        except:
                            errors.update({'value': 'Should be "DD/MM/YYYY, DD/MM/YYYY"'})

                    else:
                        try:
                            str_as_date(value)
                        except:
                            errors.update({'value': 'Should be "DD/MM/YYYY"'})


                if lookup in ('lt', 'gt', 'lte', 'gte'):
                    pass

        if errors:
            raise ValidationError(errors)


class DynamicFilterTermInline(SortableInlineAdminMixin, DynamicFilterInline):
    model = DynamicFilterTerm
    form = DynamicFilterTermInlineForm
    # formset = DynamicFilterTermInlineFormSet
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


def get_model_choices():
    return [
        (
            get_qualified_model_name(opts),
            get_model_name(opts)
        )
        for model in apps.get_models()
        if has_dynfilter(model, (opts := model._meta))
    ]

def get_next_url(request):
    f = furl(request.META["HTTP_REFERER"])
    return f.args.get('next')

@admin.register(DynamicFilterExpr)
class DynamicFilterExprAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = [DynamicFilterTermInline, DynamicFilterColumnInline, DynamicFilterColumnSortOrderInline]

    list_per_page = 50

    list_display = (
        '_name',
        'model',
        '_creator',
    )

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
        url = get_next_url(request)
        return (
            redirect(url)
            if url else
            super().response_add(request, obj, post_url_continue)
        )

    def response_change(self, request, obj):
        url = get_next_url(request)
        return (
            redirect(url)
            if url else
            super().response_change(request, obj)
        )

    # def response_delete(self, request, obj_display, obj_id):
    #     url = get_next_url(request)
    #     return (
    #         redirect(url)
    #         if url else
    #         super().response_delete(request, obj_display, obj_id)
    #     )

    def _creator(self, obj):
        return obj.user

    def _name(self, obj):
        return format_html(f'<a href="/admin/dynfilters/dynamicfilterexpr/{obj.id}/change/">{obj.name}</a>')
