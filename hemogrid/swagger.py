import logging
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg import openapi

logger = logging.getLogger(__name__)


class SafeOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    """
    A defensive schema generator that avoids bringing down the entire
    schema when an endpoint raises during inspection. As a last resort,
    it returns an empty set of endpoints/paths instead of a 500 error.
    """

    def get_endpoints(self, request):
        try:
            return super().get_endpoints(request)
        except Exception as exc:
            logger.exception("drf-yasg: failed to collect endpoints: %s", exc)
            # Fallback to no endpoints to keep the UI responsive
            return {}

    def get_paths(self, endpoints, components, request, public):
        try:
            return super().get_paths(endpoints, components, request, public)
        except Exception as exc:
            logger.exception("drf-yasg: failed to build paths: %s", exc)
            return openapi.Paths(paths={})

