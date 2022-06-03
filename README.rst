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

**models.py**

.. code-block:: python

    class Address(models.Model):
        town = models.CharField()

    class Person(models.Model):
        first_name = models.CharField()
        last_name = models.CharField()
        birth_date = models.DateField()
        address = models.ForeignKey(Address)

        class DynamicFilterMeta:
            dynamic_list_filter = {
                'select_related': ('address'),          # Optional
                'prefetch_related': (),                 # Optional
                'fields': [
                    ('-', '---------'),
                    ('first_name', 'First name'),
                    ('last_name', 'Family name'),
                    ('birth_date', 'Date of birth'), 
                    ('-', '---------'),
                    ('address__town', 'City'),
                ],
            }

**admin.py**

.. code-block:: python

    from dynfilters.filters import DynamicFilter

    @admin.register(Person)
    class PersonAdmin(admin.ModelAdmin):
        ...
        list_filter = (DynamicFilter,)

Operators & Lookups
-------------------

The following operators and lookups are supported:

**operators**

.. code-block:: python

    OP_CHOICES = [
        ('-', '-'),
        ('!', 'NOT'),
        ('&', 'AND'),
        ('|', 'OR'),
        ('(', '('),
        (')', ')'),
    ]

**lookups**

.. code-block:: python

    LOOKUP_CHOICES = [
        ('-', '---------'),
        ('=', 'Equals'),
        ('icontains', 'Contains'),
        ('istartswith', 'Starts with'),
        ('iendswith', 'Ends with'),
        ('in', 'One of'),
        ('-', '---------'),
        ('range', 'Date Range'),                # Requires the value to be: DD/MM/YYYY,DD/MM/YYYY
        ('year', 'Date Year'),                  # Requires the value to be: DD/MM/YYYY
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

Similar Packages
----------------

* Dynfilters was inspired by `django-advanced-filters`_, but I wanted something simpler that worked with existing admin forms and inlines and required less code.
* Another interesting package is `django-filter`_.
* And yet another one is `django-admin-search-builder`_.

.. _django-advanced-filters : https://github.com/modlinltd/django-advanced-filters
.. _django-filter : https://github.com/carltongibson/django-filter
.. _django-admin-search-builder : https://github.com/peppelinux/django-admin-search-builder
