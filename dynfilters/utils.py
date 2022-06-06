import collections
import datetime
import itertools

from django.apps import apps
from django.contrib import admin


def get_model_name(opts):
    return opts.model_name.capitalize()

def get_qualified_model_name(opts):
    return f'{opts.app_label}.{opts.model_name.capitalize()}'

def get_model_obj(obj):
    app_label, model_name = obj.model.split('.')
    return apps.get_model(app_label, model_name)

def get_model_admin(obj):
    model_obj = get_model_obj(obj)
    return admin.site._registry.get(model_obj)


def has_dynfilter(model_obj, opts):
    model_admin = admin.site._registry.get(model_obj)
    return hasattr(model_admin, 'dynfilters_fields') and not opts.proxy

def get_dynfilters_fields(model_admin):
    return getattr(model_admin, 'dynfilters_fields', [])

def get_dynfilters_select_related(model_admin):
    return getattr(model_admin, 'dynfilters_select_related', [])

def get_dynfilters_prefetch_related(model_admin):
    return getattr(model_admin, 'dynfilters_prefetch_related', [])


def str_as_date(value):
    return datetime.datetime.strptime(value, '%d/%m/%Y').date()

def str_as_date_range(value):
    d1, d2 = value.split(',')
    d1, d2 = d1.strip(), d2.strip()

    return [
        datetime.datetime.strptime(d1, '%d/%m/%Y').date(),
        datetime.datetime.strptime(d2, '%d/%m/%Y').date(),
    ]


def flatten(iterable, ltypes=collections.Iterable):
    remainder = iter(iterable)
    while True:
        try:
            first = next(remainder)
        except StopIteration:
            return
        if isinstance(first, ltypes) and not isinstance(first, (str,)):
            remainder = itertools.chain(first, remainder)
        else:
            yield first
