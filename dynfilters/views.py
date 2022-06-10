from furl import furl

from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect

from .clone import clone_object
from .helpers import get_model_obj
from .models import DynamicFilterExpr


def dynfilters_add(request, name):
    try:
        model_obj = get_model_obj(name)
    except:
        return HttpResponse('This model does not exist.')

    expr = DynamicFilterExpr.objects.create(
        model=name,
        user=request.user,
    )

    url = reverse('admin:dynfilters_dynamicfilterexpr_change', args=(expr.pk,))

    return redirect(f'{url}?next={request.GET.get("next")}')

def dynfilters_share(request, id):
    try:
        expr = DynamicFilterExpr.objects.get(pk=id)
    except DynamicFilterExpr.DoesNotExist:
        return HttpResponse('This filter does not exist.')

    clone = clone_object(expr)
    clone.user = request.user
    clone.save()

    url = reverse('admin:dynfilters_dynamicfilterexpr_change', args=(clone.pk,))
    
    return redirect(url)

def dynfilters_delete(request, id):
    try:
        expr = DynamicFilterExpr.objects.get(pk=id)
    except DynamicFilterExpr.DoesNotExist:
        return HttpResponse('This filter does not exist.')

    expr.delete()

    return redirect(request.META["HTTP_REFERER"])
