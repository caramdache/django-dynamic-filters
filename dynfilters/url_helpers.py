from furl import furl

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode


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

def redirect_to_referer_next(request, response):
    _next = (
        furl(referer(request))
            .args
            .get('next')
    )

    if _next:
        return redirect(_next)

    return response
