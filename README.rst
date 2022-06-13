======================
Django Dynamic Filters
======================

|Package| |License| |Downloads| |Python| |Django|

.. |Package| image:: https://badge.fury.io/py/django-dynamic-filters.svg
   :target: https://pypi.python.org/pypi/django-dynamic-filters
.. |License| image:: https://img.shields.io/pypi/l/django-dynamic-filters.svg
   :target: https://raw.githubusercontent.com/caramdache/django-dynamic-filters/main/LICENSE
.. |Downloads| image:: https://img.shields.io/pypi/dm/django-dynamic-filters.svg
   :target: https://pypi.python.org/pypi/django-dynamic-filters
.. |Python| image:: https://img.shields.io/pypi/pyversions/django-dynamic-filters.svg
   :target: https://pypi.python.org/pypi/django-dynamic-filters
.. |Django| image:: https://img.shields.io/badge/django%20versions-4.0-blue.svg
   :target: https://www.djangoproject.com

A django ModelAdmin Filter which adds advanced filtering abilities to the admin.

**creating filters**

.. figure:: https://github.com/caramdache/django-dynamic-filters/raw/main/images/filter_edit.png
   :alt: Creating a filter
   :width: 768 px

**using filters**

.. figure:: https://github.com/caramdache/django-dynamic-filters/raw/main/images/filter_user.png
   :alt: Apply a filter
   :width: 768 px
   
Requirements
------------

* Django >= 4.0 on Python 3.9+/PyPy3
* django-admin-sortable2_ and furl_

.. _django-admin-sortable2 : https://github.com/jrief/django-admin-sortable2
.. _furl : https://github.com/gruns/furl

Installation & Set up
---------------------

1. Run ``pip install django-dynamic-filters`` to install dynfilters.

2. Add "dynfilters" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'adminsortable2',
        'dynfilters',
    ]

3. Add "dynfilters" URL to your urls.py file::

    urlpatterns = [
        ...
        path('dynfilters/', include('dynfilters.urls')),
    ]

4. Run ``python manage.py migrate`` to create the dynfilters models.

Integration Example
-------------------

**models.py**

.. code-block:: python

    class Address(models.Model):
        town = models.CharField(max_length=32)

    class Person(models.Model):
        first_name = models.CharField(max_length=32)
        last_name = models.CharField(max_length=32)
        birth_date = models.DateField()
        address = models.ForeignKey(Address, on_delete=models.CASCADE)

**admin.py**

.. code-block:: python

    from dynfilters.filters import DynamicFilter

    @admin.register(Person)
    class PersonAdmin(admin.ModelAdmin):
        ...
        list_filter = (DynamicFilter,)

        dynfilters_fields = [
            '-',
            'first_name',
            'last_name',
            'first_name|last_name',             # Will generate Q(first_name=<value>) | Q(last_name=<value>)
            ('birth_date', 'Date of birth'),    # Requires the value to be: DD/MM/YYYY
            '-',
            ('address__town', 'City'),
        ]

        dynfilters_select_related = ['address'] # Optional
        dynfilters_prefetch_related = []        # Optional
        
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
        ('in', 'One of'),          # Requires the value to be: aaa,bbb,ccc
        ('-', '---------'),
        ('range', 'Date Range'),   # Requires the value to be: DD/MM/YYYY,DD/MM/YYYY
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

Sharing
-------

There are two ways dynamic filters can be shared:

1. By marking a filter `global`. The filter will then be available to all admin users.

2. By pressing the `share` icon. The filter will then be shared by email. When the recipients clicks on the received link, a copy of the filter will be created. The edits made to the copy will not affect the original filter.

Alternatives
------------

* Dynfilters was inspired by the look and feel of `django-advanced-filters`_, but is based purely on admin forms and inlines (no JSON).
* Another interesting package is `django-filter`_.
* And yet another one is `django-admin-search-builder`_.

.. _django-advanced-filters : https://github.com/modlinltd/django-advanced-filters
.. _django-filter : https://github.com/carltongibson/django-filter
.. _django-admin-search-builder : https://github.com/peppelinux/django-admin-search-builder
