from itertools import tee, chain

from django.apps import apps
from django.contrib.auth.models import User
from django.db import connection
from django.db import models
from django.db.models import Q
from django.db.models.deletion import CASCADE, SET_NULL
from django.db.models.sql.compiler import SQLCompiler
from django.db.models.sql.query import Query
from django.utils.translation import gettext_lazy as _

from .utils import (
    get_model_admin,
    get_model_obj,
    flatten,
    str_as_date, 
    str_as_date_range, 
)


def get_dynamic_list_filter_queryset(obj, queryset):
    model_admin = get_model_admin(obj)

    fields = flatten([
        f[0].split('__') 
        for f in getattr(model_admin, 'dynfilters_fields', [])
        if f[0] != '-'
    ])

    select_related = [
        f 
        for f in getattr(model_admin, 'dynfilters_select_related', [])
        if f in fields
    ]

    prefetch_related = [
        f 
        for f in getattr(model_admin, 'dynfilters_prefetch_related', [])
        if f in fields
    ]

    # return (
    #     queryset
    #         .select_related(*select_related)
    #         .prefetch_related(*prefetch_related)
    #         .filter(obj.as_q())
    # )

    return queryset.filter(obj.as_q())


class DynamicFilterExpr(models.Model):
    class Meta:
        verbose_name = 'Filter'
        verbose_name_plural = 'Filters'

    name = models.CharField(max_length=128, default='Report')
    model = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_global = models.BooleanField(default=False)

    def __str__(self):
        return self.as_sql()

    #     return '\n'.join([
    #         str(term) 
    #         for term in self.normalized_terms()
    #     ])

    def execute(self):
        model_obj = get_model_obj(self)

        return get_dynamic_list_filter_queryset(
            model_obj,
            model_obj.objects.all(),
        )

    # Make implicit operators explicit to
    # ensure the ops stack is never empty.
    def normalized_terms(self):
        # https://stackoverflow.com/questions/1011938/loop-that-also-accesses-prev-and-next-values
        def previous(some_iterable):
            prevs, items = tee(some_iterable, 2)
            prevs = chain([None], prevs)
            return zip(prevs, items)

        nterms = []

        for prev, item in previous(self.dynamicfilterterm_set.all()):
            if prev:
                # Add implicit ANDs.
                if prev.op in ('-', '!', ')') and item.op in ('-', '!', '('):
                    nterms.append(DynamicFilterTerm(op='&'))

                # Add no-ops.
                elif prev.op in ('(', '&', '|') and item.op in (')', '&', '|'):
                    nterms.append(DynamicFilterTerm(op=' '))

            nterms.append(item)

        if not nterms:
            # Add no-op to avoid empty filter.
            nterms.append(DynamicFilterTerm(op=' '))

        return nterms

    def as_sql(self):
        model_obj = get_model_obj(self)
        query = Query(model_obj)

        where = self.as_q().resolve_expression(query)
        
        compiler = query.get_compiler(using='default')
        query_str, args = where.as_sql(compiler, connection)

        return query_str % tuple(args)

    # Function that returns value of
    # expression after evaluation.
    # Adapted from https://www.geeksforgeeks.org/expression-evaluation/
    def as_q(self):
        # Function to find precedence 
        # of operators.
        def precedence(op): 
            if op == ' ': return 3 # no-op
            if op == '&': return 2 # AND
            if op == '|': return 1 # OR
            return 0
         
        # Function to perform arithmetic 
        # operations.
        def popAndApplyOp():
            op = ops.pop()

            # no-op
            if op == ' ': return Q()

            b = values.pop()
            a = values.pop()

            # AND | OR
            if op == '&': return a & b
            if op == '|':  return a | b

        # stack to store Q objects.
        values = []

        # stack to store operators.
        ops = []

        for token in self.normalized_terms():

            # Current token is an opening 
            # brace, push it to 'ops'
            if token.op == '(':
                ops.append(token.op)

            # Current token is a term, push 
            # it to stack for Q objects.
            elif token.op == "-" or token.op == '!':
                values.append(token.as_q())
              
            # Closing brace encountered, 
            # solve entire brace.
            elif token.op == ')':
                while ops and ops[-1] != '(':
                    values.append(popAndApplyOp())
                
                # pop opening brace.
                ops.pop()
            
            # Current token is an operator.
            else:
                # While top of 'ops' has same or 
                # greater precedence to current 
                # token, which is an operator.
                # Apply operator on top of 'ops' 
                # to top two elements in values stack.
                while (ops and
                    precedence(ops[-1]) >=
                    precedence(token.op)):
                            
                    values.append(popAndApplyOp())
                
                # Push current token to 'ops'.
                ops.append(token.op)
            
        # Entire expression has been parsed 
        # at this point, apply remaining ops 
        # to remaining values.
        while ops:            
            values.append(popAndApplyOp())

        # Top of 'values' contains result, 
        # return it.
        return values[-1]


class DynamicFilterTerm(models.Model):
    OP_CHOICES = [
        ('-', '-'),
        ('!', 'NOT'),
        ('&', 'AND'),
        ('|', 'OR'),
        ('(', '('),
        (')', ')'),
    ]

    LOOKUP_CHOICES = [
        ('-', '---------'),
        ('=', 'Equals'),
        ('icontains', 'Contains'),
        ('istartswith', 'Starts with'),
        ('iendswith', 'Ends with'),
        ('in', 'One of'),
        # ('iregex', 'One of'),
        ('-', '---------'),
        ('range', 'Date Range'),
        ('year', 'Date Year'),
        ('month', 'Date Month'),
        ('day', 'Date Day'),
        ('-', '---------'),
        ('isnull', 'Is NULL'),
        ('isnotnull', 'Is not NULL'),
        ('istrue', 'Is TRUE'),
        ('isfalse', 'Is FALSE'),
        ('-', '---------'),
        ('lt', 'Less Than'),
        ('gt', 'Greater Than'),
        ('lte', 'Less Than or Equal To'),
        ('gte', 'Greater Than or Equal To'),
    ]

    class Meta:
        ordering = ('order',)
        verbose_name = 'Field'
        verbose_name_plural = 'Fields'

    filter = models.ForeignKey(DynamicFilterExpr, on_delete=CASCADE)
    op = models.CharField(max_length=1, choices=OP_CHOICES, default='-')
    field = models.CharField(max_length=64, blank=True, null=True)
    lookup = models.CharField(max_length=16, choices=LOOKUP_CHOICES, default='-')
    value = models.CharField(max_length=100, blank=True, null=True)
    bilateral = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0, blank=True, db_index=True)

    def __str__(self):
        if self.op in ('-', '!'):
            comparison = '!=' if self.op == '!' else '=='
            return f'{self.field}__{self.lookup} {comparison} {self.value}'
        else:
            return self.op

    def clean(self):
        if self.op in ('&', '|', '(', ')'):
            self.field = '-'
            self.lookup = '-'
            self.value = None

        elif self.op in ('-', '!'):
            if self.lookup in ('isnull', 'isnotnull', 'istrue', 'isfalse'):
                self.value = None

    def get_keypath(self):
        if self.lookup in ('=', 'istrue', 'isfalse'):
            return self.field

        if self.lookup in ('isnull', 'isnotnull'):
            return f'{self.field}__isnull'

        return f'{self.field}__{self.lookup}'

    def get_value(self):
        if self.lookup in ('isnull', 'istrue'):
            return True

        if self.lookup in ('isnotnull', 'isfalse'):
            return False

        if self.lookup == 'in':
            return self.value.split(',')

        if self.lookup == 'range':
            return str_as_date_range(self.value)

        if 'date' in self.field:
            return str_as_date(self.value)

        return self.value

    def as_q(self):
        if self.lookup == '-' or self.value == '-':
            return Q()

        term = {self.get_keypath(): self.get_value()}

        return (
            ~Q(**term)
            if self.op == '!' else
            Q(**term)
        )


class DynamicFilterColumn(models.Model):
    class Meta:
        ordering = ('order',)
        verbose_name = 'Column'
        verbose_name_plural = 'Columns'

    filter = models.ForeignKey(DynamicFilterExpr, on_delete=CASCADE)
    field = models.CharField(max_length=64, blank=True, null=True)
    order = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.field


class DynamicFilterColumnSortOrder(models.Model):
    class Meta:
        ordering = ('order',)
        verbose_name = 'Column sort order'
        verbose_name_plural = 'Column sort orders'

    filter = models.ForeignKey(DynamicFilterExpr, on_delete=CASCADE)
    field = models.CharField(max_length=64, blank=True, null=True)
    order = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.field
