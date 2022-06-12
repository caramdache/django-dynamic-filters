from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse

from .model_helpers import (
    get_model_admin,
    get_qualified_model_names,
    get_dynfilters_fields,
    get_dynfilters_select_related,
    get_dynfilters_prefetch_related,
)
from .models import DynamicFilterExpr
from .utils import flatten


class DynamicFilter(admin.SimpleListFilter):
    title = 'dynamic filter'
    parameter_name = "filter"
    template = 'dynfilters/dynamic_filter.html'

    email_subject = 'Sharing filter'
    email_text = 'Hi,\nI would like to share this filter with you:\n\n'

    def __init__(self, request, params, model, model_admin):
        self.request = request
        self.model_name = get_qualified_model_names(model._meta)[0]

        return super().__init__(request, params, model, model_admin)

    def has_output(self):
        return True

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": "All",
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
                "lookup": lookup,
                "email_body": self.request.build_absolute_uri(
                    reverse('dynfilters_share', args=(lookup,))
                ),
            }

    def lookups(self, request, model_admin):
        model_names = get_qualified_model_names(model_admin.opts)
        
        return [
            (o.pk, o.name)
            for o in (
                DynamicFilterExpr
                    .objects
                    .filter(model__in=model_names)
                    .filter(Q(user=request.user) | Q(is_global=True))
                    .order_by('name')
                )
        ]

    def queryset(self, request, queryset):
        if self.value() is not None:
            try:
                obj = DynamicFilterExpr.objects.get(pk=self.value())
            except DynamicFilterExpr.DoesNotExist:
                return queryset # filter no longer exists

            model_admin = get_model_admin(obj)

            elementary_fields = flatten([
                f.split('__') 
                for f, display in get_dynfilters_fields(model_admin)
                if f != '-'
            ])

            queryset = queryset.select_related(*[
                f 
                for f in get_dynfilters_select_related(model_admin)
                if f in elementary_fields
            ])

            queryset = queryset.prefetch_related(*[
                f 
                for f in get_dynfilters_prefetch_related(model_admin)
                if f in elementary_fields
            ])

            try:
                return queryset.filter(obj.as_q())
            except:
                messages.error(request, 'The selected filter is buggy and cannot be applied.')
                return queryset
