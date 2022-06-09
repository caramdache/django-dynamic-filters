from django.http import HttpResponse
from django.shortcuts import redirect

from .models import DynamicFilterExpr
from .clone import clone_object


def dynfilters_share(request, id):
    try:
        expr = DynamicFilterExpr.objects.get(pk=id)

    except DynamicFilterExpr.DoesNotExist:
        return HttpResponse('This filter does not exist.')

    clone = clone_object(expr)
    clone.user = request.user
    clone.save()

    return redirect(f'/admin/dynfilters/dynamicfilterexpr/{clone.pk}/change/')
