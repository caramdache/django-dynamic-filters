from itertools import tee, chain
import collections
import datetime
import itertools


def str_as_date(value):
    return datetime.datetime.strptime(value, '%d/%m/%Y').date()

def str_as_date_range(value):
    d1, d2 = value.split(',')
    d1, d2 = d1.strip(), d2.strip()

    return [
        datetime.datetime.strptime(d1, '%d/%m/%Y').date(),
        datetime.datetime.strptime(d2, '%d/%m/%Y').date(),
    ]


def previous(some_iterable):
    prevs, items = tee(some_iterable, 2)
    prevs = chain([None], prevs)
    return zip(prevs, items)


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


def to_int(value):
    if isinstance(value, (int, float)):
        return int(value)

    if isinstance(value, str) and value.isdigit():
        return int(value)

    if isinstance(value, (list, tuple)):
        for s in value:
            if s.isdigit():
                return int(s)

    return None
