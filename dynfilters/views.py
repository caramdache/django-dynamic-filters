from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .clone import clone_object
from .helpers import get_model_obj
from .models import DynamicFilterExpr


def referer(request):
    return request.META["HTTP_REFERER"]

def redirect_to_referer(request):
    return redirect(referer(request))


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

    url = reverse('admin:dynfilters_dynamicfilterexpr_change', args=(expr.id,))
    return redirect(f'{url}?next={referer(request)}')

def dynfilters_share(request, id):
    try:
        expr = DynamicFilterExpr.objects.get(pk=id)
    except DynamicFilterExpr.DoesNotExist:
        messages.error(request, 'This filter does not exist.')
        return redirect(reverse('admin:dynfilters_dynamicfilterexpr_changelist'))

    clone = clone_object(expr)
    clone.user = request.user
    clone.save()

    return redirect(reverse('admin:dynfilters_dynamicfilterexpr_change', args=(clone.id,)))

def dynfilters_change(request, id):
    url = reverse('admin:dynfilters_dynamicfilterexpr_change', args=(id,))
    return redirect(f'{url}?next={referer(request)}')

def dynfilters_delete(request, id):
    try:
        expr = DynamicFilterExpr.objects.get(pk=id)
    except DynamicFilterExpr.DoesNotExist:
        messages.error(request, 'This filter does not exist.')
        return redirect_to_referer(request)

    expr.delete()

    return redirect_to_referer(request)
