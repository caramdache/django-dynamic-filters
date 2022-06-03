======================
Django Dynamic Filters
======================

A django ModelAdmin Filter which adds advanced filtering abilities to the admin.

Requirements
------------

* Django >= 4.0 on Python 3.9+/PyPy3
* furl
* django-admin-sortable2

Installation & Set up
---------------------

1. Run ``pip install django-dynamic-filters`` to install dynfilters.

2. Add "dynfilters" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'dynfilters',
    ]

3. Run ``python manage.py migrate`` to create the dynfilters models.

Integration Example
-------------------

Extending a ModelAdmin is straightforward:

*models.py*
```

class Address(models.Model):
    town = models.CharField()

class Person(models.Model):
    first_name = models.CharField()
    last_name = models.CharField()
    birth_date = models.DateField()
    is_married = models.BooleanField()
    address = models.ForeignKey(Address)

    class DynamicFilterMeta:
        dynamic_list_filter = {
            'select_related': ('address'),
            'prefetch_related': (),
            'fields': [
                ('-', '---------'),
                ('first_name', 'First name'),
                ('last_name', 'Family name'),
                ('is_married', 'Married?'),      # '?' in display text will mean field will be handled as boolean in queryset
                ('birth_date', 'Date of birth'), # 'date' in field name will mean field will be handle as boolean in querset
                ('-', '---------'),
                ('address__town', 'City'),
            ],
        }

```

*admin.py*
```

from dynfilters.filters import DynamicFilter

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    ...
    dynamic_list_filter_modelname = 'myApp.Person'
    list_filter = (DynamicFilter,)

```

Similar Packages
----------------

* Dynfilters was inspired by `django-advanced-filters`_, but I wanted something simpler that would require as few changes as possible to the django admin.
* Another interesting package is `django-filter`_.

.. _django-advanced-filters : https://github.com/modlinltd/django-advanced-filters
.. _django-filter : https://github.com/carltongibson/django-filter
