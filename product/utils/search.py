from rest_framework import filters
from django.db.models import Q
from functools import reduce
from operator import or_
import re

class AdvancedSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        return request.GET.getlist('search_fields', ['name', 'description', 'category__title'])

    def get_search_terms(self, request):
        params = request.query_params.get(self.search_param, '')
        params = params.replace('\x00', '')
        params = params.replace(',', ' ')
        return params.split()

    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)
        if not search_terms:
            return queryset

        search_fields = self.get_search_fields(view, request)
        base_query = None

        for search_term in search_terms:
            queries = []
            
            for field in search_fields:
                exact_query = Q(**{f"{field}__iexact": search_term})
                queries.append((exact_query, 1.0))

            for field in search_fields:
                starts_with_query = Q(**{f"{field}__istartswith": search_term})
                queries.append((starts_with_query, 0.8))

            for field in search_fields:
                contains_query = Q(**{f"{field}__icontains": search_term})
                queries.append((contains_query, 0.6))

            for field in search_fields:
                similar_query = Q(**{f"{field}__iregex": f".*{search_term}.*"})
                queries.append((similar_query, 0.4))

            term_query = reduce(or_, [q[0] for q in queries])
            if base_query is None:
                base_query = term_query
            else:
                base_query &= term_query

        return queryset.filter(base_query).distinct() 