======================
Django Dynamic Filters
======================

A django ModelAdmin mixin which adds advanced filtering abilities to the admin.

Requirements
------------

* Django >= 4.0 on Python 3.9+/PyPy3

Installation & Set up
---------------------

1. Run ``pip install django-dynamic-filters`` to install dynfilters.

2. Add "dynfilters" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'dynfilters',
    ]

3. Include the dynfilters URLconf in your project urls.py like this::

    path('dynfilters/', include('dynfilters.urls')),

4. Run ``python manage.py migrate`` to create the dynfilters models.

Integration Example
-------------------

Extending a ModelAdmin is straightforward:

```python
from dynfilters.admin import AdminDynamicFiltersMixin

class ProfileAdmin(AdminDynamicFiltersMixin, models.ModelAdmin):
    list_filter = ('name', 'language', 'ts')   # simple list filters

    # specify which fields can be selected in the advanced filter
    # creation form
    advanced_filter_fields = (
        'name',
        'language',
        'ts',

        # even use related fields as lookup fields
        'country__name',
        'posts__title',
        'comments__content',
    )
```
