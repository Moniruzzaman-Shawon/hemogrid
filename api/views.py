# api/views.py
from django.urls import get_resolver, URLPattern, URLResolver
from rest_framework.decorators import api_view
from rest_framework.response import Response

def list_urls(lis, parent_pattern=''):
    grouped_urls = {}

    for item in lis:
        if isinstance(item, URLPattern):
            # Determine the app name from the pattern (or use 'General')
            app_name = getattr(item.callback, 'cls', None)  # For class-based views
            if hasattr(app_name, '__module__'):
                app_name = app_name.__module__.split('.')[0]
            else:
                app_name = 'General'

            if app_name not in grouped_urls:
                grouped_urls[app_name] = {}

            name = item.name or str(item.pattern)
            path_ = parent_pattern + str(item.pattern)
            grouped_urls[app_name][name] = '/' + path_

        elif isinstance(item, URLResolver):
            nested = list_urls(item.url_patterns, parent_pattern + str(item.pattern))
            # Merge nested URLs into grouped_urls
            for k, v in nested.items():
                if k not in grouped_urls:
                    grouped_urls[k] = {}
                grouped_urls[k].update(v)

    return grouped_urls

@api_view(['GET'])
def api_home(request):
    resolver = get_resolver()
    grouped_urls = list_urls(resolver.url_patterns)
    return Response(grouped_urls)
