from django.apps import apps
from django.contrib import admin


def get_model_name(opts):
    return opts.model_name.capitalize()

def get_qualified_model_name(opts):
    return f'{opts.app_label}.{opts.model_name.capitalize()}'

def get_qualified_model_names(opts):
    # The model may be a proxy on a different site, so we need to consider parents also
    names = [
        get_qualified_model_name(meta)
        for parent in opts.get_parent_list() 
        if (meta := parent._meta)
    ]

    names.append(
        get_qualified_model_name(opts)
    )

    return names

def get_model_obj(qmodel_name):
    app_label, model_name = qmodel_name.split('.')
    return apps.get_model(app_label, model_name)

def get_model_admin(obj):
    model_obj = get_model_obj(obj.model)
    return admin.site._registry.get(model_obj)

def get_model_choices():
    return [
        (
            get_qualified_model_name(opts),
            get_model_name(opts)
        )
        for model_obj in apps.get_models()
        if has_dynfilter(model_obj, (opts := model_obj._meta))
    ]


def has_dynfilter(model_obj, opts):
    model_admin = admin.site._registry.get(model_obj)
    return hasattr(model_admin, 'dynfilters_fields') and not opts.proxy

def get_dynfilters_fields(model_admin):
    def humanize(f):
        if f == '-':
            return ('-', '---------')

        if isinstance(f, str):
            return (
                f, 
                ' OR '.join([
                    s.replace('__', ' ').replace('_', ' ').capitalize() 
                    for s in f.split('|')
                ])
            )

        return f

    fields = getattr(model_admin, 'dynfilters_fields', [])
    return [humanize(f) for f in fields]

def get_dynfilters_select_related(model_admin):
    return getattr(model_admin, 'dynfilters_select_related', [])

def get_dynfilters_prefetch_related(model_admin):
    return getattr(model_admin, 'dynfilters_prefetch_related', [])
