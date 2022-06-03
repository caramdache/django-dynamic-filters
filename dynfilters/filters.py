from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User

from .models import DynamicFilterExpr, get_dynamic_list_filter_queryset


class DynamicFilter(admin.SimpleListFilter):
    title = 'filter'
    parameter_name = "filter"
    template = 'dynfilters/dynamic_filter.html'

    def __init__(self, request, params, model, model_admin):
        self.path = request.path
        self.model_name = model_admin.dynamic_list_filter_modelname
        return super().__init__(request, params, model, model_admin)

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": "All",
            "lookup": self.model_name,
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
        if not request.user.is_admin:
            return tuple()

        return [
            (o.pk, o.name)
            for o in (
                DynamicFilterExpr
                    .objects
                    .filter(model=self.model_name)
                    .filter(user=request.user)
                    .order_by('name')
                )
        ]

    def queryset(self, request, queryset):
        if self.value() is not None:
            try:
                obj = DynamicFilterExpr.objects.get(pk=self.value())
                return get_dynamic_list_filter_queryset(obj, queryset)
            
            except DynamicFilterExpr.DoesNotExist:
                return queryset
