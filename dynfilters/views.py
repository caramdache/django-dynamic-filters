from django.contrib import messages

from .clone import clone_object
from .model_helpers import get_model_obj
from .models import DynamicFilterExpr
from .url_helpers import (
    referer,
    redirect_to_referer,
    redirect_to_changelist,
    redirect_to_change,
)


def dynfilters_add(request, model_name):
    try:
        model_obj = get_model_obj(model_name)
    except:
        messages.error(request, 'This type of model is unknown.')
        return redirect_to_referer(request)

    expr = DynamicFilterExpr.objects.create(
        model=model_name,
        user=request.user,
    )

    return redirect_to_change(request, expr.id, follow=True)

def dynfilters_share(request, id):
    try:
        expr = DynamicFilterExpr.objects.get(pk=id)
    except DynamicFilterExpr.DoesNotExist:
        messages.error(request, 'This filter does not exist.')
        return redirect_to_changelist(request)

    clone = clone_object(expr)
    clone.user = request.user
    clone.save()

    return redirect_to_change(request, clone.id)

def dynfilters_change(request, id):
    return redirect_to_change(request, id, follow=True)

def dynfilters_delete(request, id):
    try:
        expr = DynamicFilterExpr.objects.get(pk=id)
    except DynamicFilterExpr.DoesNotExist:
        messages.error(request, 'This filter does not exist.')
        return redirect_to_referer(request)

    expr.delete()

    return redirect_to_referer(request)
