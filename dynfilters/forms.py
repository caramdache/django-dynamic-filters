from furl import furl
from operator import itemgetter

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from adminsortable2.admin import CustomInlineFormSet

from .models import DynamicFilterExpr, DynamicFilterTerm
from .utils import (
    to_int,
    str_as_date, 
    str_as_date_range, 
    clone_instance,
    clone_related,
)


class DynamicFilterExprForm(forms.ModelForm):
    class Meta:
        model = DynamicFilterExpr
        fields = ('name', 'model', 'user')

    sharee = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Share copy with',
        required=False,
    )

    def clean_sharee(self):
        sharee = self.cleaned_data.get('sharee')
        
        if sharee:
            f = furl(self.referer_uri)
            pk = to_int(f.path.segments)

            expr = DynamicFilterExpr.objects.get(pk=pk)
            terms = list(expr.dynamicfilterterm_set.all())
            columns = list(expr.dynamicfiltercolumn_set.all())
            sorts = list(expr.dynamicfiltercolumnsortorder_set.all())
            
            expr.user = sharee
            clone = clone_instance(expr)
            clone_related(terms, 'filter', clone)
            clone_related(columns, 'filter', clone)
            clone_related(sorts, 'filter', clone)


class DynamicFilterTermInlineFormSet(CustomInlineFormSet):
    def clean(self):
        i = 0

        for form in self.forms:
            _del = form.cleaned_data.get('DELETE')
            if _del:
                continue

            op = form.cleaned_data.get('op')
            if op == '(':
                i += 1
            elif op == ')':
                i -= 1

            if i < 0:
                raise ValidationError("Missing opening parenthesis")

        if i:
            raise ValidationError("Missing closing parenthesis")


class DynamicFilterTermInlineForm(forms.ModelForm):
    class Meta:
        model = DynamicFilterTerm
        fields = ('op', 'field', 'lookup', 'value', 'order')

    def clean(self):
        errors = {}

        op, field, lookup, value = itemgetter('op', 'field', 'lookup', 'value')(self.cleaned_data)

        if op in ('-', '!'):
            if field == '-':
                errors.update({'field': 'Missing value'})

            if lookup == '-':
                errors.update({'lookup': 'Missing value'})

            if not value:
                if lookup not in ('isnull', 'isnotnull', 'istrue', 'isfalse'):
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


                if lookup in ('year', 'month', 'day', 'lt', 'gt', 'lte', 'gte'):
                    try:
                        float(value)
                    except:
                        errors.update({'value': 'Should be a number'})

        else:
            pass # will be handled by model clean()

        if errors:
            raise ValidationError(errors)
