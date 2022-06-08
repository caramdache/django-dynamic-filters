from operator import itemgetter

from django import forms
from django.core.exceptions import ValidationError

from adminsortable2.admin import CustomInlineFormSet

from .models import DynamicFilterTerm
from .utils import str_as_date, str_as_date_range


class DynamicFilterTermInlineFormSet(CustomInlineFormSet):
    pass


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

        if errors:
            raise ValidationError(errors)
