# https://stackoverflow.com/a/61729857/2893408
# https://github.com/morlandi/test-django-clone

def clone_object(obj, attrs={}):
    # we start by building a "flat" clone
    clone = obj._meta.model.objects.get(id=obj.id)
    clone.id = None

    # if caller specified some attributes to be overridden, use them
    for key, value in attrs.items():
        setattr(clone, key, value)

    # save the partial clone to have a valid ID assigned
    clone.save()

    # Scan field to further investigate relations
    fields = clone._meta.get_fields()
    for field in fields:

        # Manage M2M fields by replicating all related records found on parent "obj" into "clone"
        if not field.auto_created and field.many_to_many:
            for row in getattr(obj, field.name).all():
                getattr(clone, field.name).add(row)

        # Manage 1-N and 1-1 relations by cloning child objects
        if field.auto_created and field.is_relation:
            if field.many_to_many:
                # do nothing
                pass
            else:
                # provide "clone" object to replace "obj" on remote field
                attrs = {
                    field.remote_field.name: clone
                }
                children = field.related_model.objects.filter(**{field.remote_field.name: obj})
                for child in children:
                    clone_object(child, attrs)

    return clone
