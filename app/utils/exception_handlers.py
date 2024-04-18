# my_project.error_handling.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    exception_class = exc.__class__.__name__

    handlers = {"TaakInGebruik": [str(exc), status.HTTP_423_LOCKED]}
    custom_handler = handlers.get(
        exception_class, ["Er ging iets mis", status.HTTP_500_INTERNAL_SERVER_ERROR]
    )

    response = exception_handler(exc, context)

    if response:
        return response
    return Response({"detail": custom_handler[0]}, status=custom_handler[1])
