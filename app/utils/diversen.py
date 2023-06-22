def absolute(request):
    urls = {
        "ABSOLUTE_ROOT": request.build_absolute_uri("/")[:-1].strip("/"),
        "FULL_URL_WITH_QUERY_STRING": request.build_absolute_uri(),
        "FULL_URL": request.build_absolute_uri("?"),
    }

    return urls
