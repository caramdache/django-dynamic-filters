from furl import furl

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode

from .clone import clone_object
from .helpers import get_model_obj
from .models import DynamicFilterExpr


def referer(request):
    return request.META["HTTP_REFERER"]

def redirect_to_referer(request):
    return redirect(referer(request))

def redirect_to_changelist(request):
    return redirect(reverse('admin:dynfilters_dynamicfilterexpr_changelist'))

def redirect_to_change(request, id, follow=False):
    url = reverse('admin:dynfilters_dynamicfilterexpr_change', args=(id,))

    if follow:
        query_string = urlencode({
            'next': (
                furl(referer(request))
                    .remove(['filter'])
                    .add({'filter': id})
                    .url
            ),
        })

        return redirect(f'{url}?{query_string}')

    return redirect(url)


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
