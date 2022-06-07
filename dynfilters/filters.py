from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User

from .models import DynamicFilterExpr
from .utils import (
    get_model_admin,
    get_qualified_model_name,
    get_dynfilters_fields,
    get_dynfilters_select_related,
    get_dynfilters_prefetch_related,
    flatten,
)


class DynamicFilter(admin.SimpleListFilter):
    title = 'filter'
    parameter_name = "filter"
    template = 'dynfilters/dynamic_filter.html'

    def __init__(self, request, params, model, model_admin):
        self.path = request.path
        return super().__init__(request, params, model, model_admin)

    def has_output(self):
        return True

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": "All",
            "request_path": self.path,
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
                "lookup": lookup,
                "request_path": self.path,
            }

    def lookups(self, request, model_admin):
        model_name = get_qualified_model_name(model_admin.opts)
        
        return [
            (o.pk, o.name)
            for o in (
                DynamicFilterExpr
                    .objects
                    .filter(model=model_name)
                    .filter(user=request.user)
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

            fields = flatten([
                f[0].split('__') 
                for f in get_dynfilters_fields(model_admin)
                if f[0] != '-'
            ])

            select_related = [
                f 
                for f in get_dynfilters_select_related(model_admin)
                if f in fields
            ]

            prefetch_related = [
                f 
                for f in get_dynfilters_prefetch_related(model_admin)
                if f in fields
            ]

            return (
                queryset
                    .select_related(*select_related)
                    .prefetch_related(*prefetch_related)
                    .filter(obj.as_q())
            )
            
