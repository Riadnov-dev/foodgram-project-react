from rest_framework.views import exception_handler
from rest_framework.exceptions import NotFound
from rest_framework.response import Response


def notfound_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, NotFound):
        return Response(
            {"count": 0, "next": None, "previous": None, "results": []},
            status=200
        )

    return response
