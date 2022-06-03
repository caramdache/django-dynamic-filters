import collections
import datetime
import itertools


def get_model_name(opts):
    return opts.model_name.capitalize()

def get_qualified_model_name(opts):
    return f'{opts.app_label}.{opts.model_name.capitalize()}'


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
