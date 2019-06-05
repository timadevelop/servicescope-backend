from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.paginator import Paginator

from django.utils.functional import cached_property

class FasterDjangoPaginator(Paginator):
    @cached_property
    def count(self):
        # only select 'id' for counting, much cheaper
        return self.object_list.values('id').count()

class MyPagination(PageNumberPagination):
    django_paginator_class = FasterDjangoPaginator
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'pages': self.page.paginator.num_pages,
            'page': self.page.number,
            'results': data
        })
