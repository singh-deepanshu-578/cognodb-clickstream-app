from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from neo4j.exceptions import ServiceUnavailable, Neo4jError
from .db import get_driver
from . import queries


def run_query(cypher, params=None):
    """Helper: run a query and return list-of-dicts, with graceful DB error handling."""
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(cypher, params or {})
            return [dict(record) for record in result], None
    except ServiceUnavailable:
        return None, "Database is currently unreachable. Please try again shortly."
    except Neo4jError as e:
        return None, f"Query error: {e.message}"


@api_view(["GET"])
def list_visitors(request):
    skip = int(request.GET.get("skip", 0))
    limit = int(request.GET.get("limit", 20))
    data, error = run_query(queries.LIST_VISITORS, {"skip": skip, "limit": limit})
    if error:
        return Response({"error": error}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({"visitors": data})


@api_view(["GET"])
def visitor_overview(request, visitor_id):
    data, error = run_query(queries.VISITOR_OVERVIEW, {"visitor_id": visitor_id})
    if error:
        return Response({"error": error}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    if not data:
        return Response({"error": "Visitor not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(data[0])


@api_view(["GET"])
def visitor_journey(request, visitor_id):
    data, error = run_query(queries.VISITOR_JOURNEY_TO_PURCHASE, {"visitor_id": visitor_id})
    if error:
        return Response({"error": error}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({"journey": data})


@api_view(["GET"])
def returning_chains(request, visitor_id):
    data, error = run_query(queries.RETURNING_VISITOR_CHAINS, {"visitor_id": visitor_id})
    if error:
        return Response({"error": error}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({"chains": data})


@api_view(["GET"])
def common_paths(request):
    data, error = run_query(queries.COMMON_THREE_PAGE_PATHS)
    if error:
        return Response({"error": error}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({"paths": data})


@api_view(["GET"])
def abandonment_points(request):
    data, error = run_query(queries.ABANDONMENT_POINTS)
    if error:
        return Response({"error": error}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({"abandonment_points": data})


@api_view(["GET"])
def also_viewed(request, product_id):
    data, error = run_query(queries.ALSO_VIEWED_BY_PURCHASERS, {"product_id": product_id})
    if error:
        return Response({"error": error}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({"also_viewed": data})


@api_view(["GET"])
def referrer_conversion(request):
    data, error = run_query(queries.REFERRER_CONVERSION)
    if error:
        return Response({"error": error}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({"referrer_conversion": data})


@api_view(["GET"])
def top_pages(request):
    data, error = run_query(queries.TOP_PAGES)
    if error:
        return Response({"error": error}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({"top_pages": data})