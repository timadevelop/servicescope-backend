import inspect

from django.core.paginator import Paginator
from django.utils.functional import cached_property
from django.utils.inspect import method_has_no_args
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FasterDjangoPaginator(Paginator):
    @cached_property
    def count(self):
        """Return the total number of objects, across all pages."""
        c = getattr(self.object_list, 'count', None)
        if callable(c) and not inspect.isbuiltin(c) and method_has_no_args(c):
            return c()
        return len(self.object_list)


class MyPagination(PageNumberPagination):
    django_paginator_class = FasterDjangoPaginator
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'pages': self.page.paginator.num_pages,
            'page': self.page.number,
            'results': data
        })
