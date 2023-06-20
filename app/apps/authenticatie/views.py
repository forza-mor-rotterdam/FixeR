from urllib import parse

import requests
from django.conf import settings


def provider_logout(request):
    print("provider_logout")
    logout_url = settings.OIDC_OP_LOGOUT_ENDPOINT

    # If we have the oidc_id_token, we can automatically redirect
    # the user back to the application.

    oidc_id_token = request.session.get("oidc_id_token", None)
    redirect_url = request.build_absolute_uri(location=settings.LOGOUT_REDIRECT_URL)
    if oidc_id_token:
        logout_url = (
            settings.OIDC_OP_LOGOUT_ENDPOINT
            + "?"
            + parse.urlencode(
                {
                    "id_token_hint": oidc_id_token,
                    "post_logout_redirect_uri": redirect_url,
                }
            )
        )
    logout_response = requests.get(logout_url)
    print(logout_response.status_code)
    print(logout_response.text)

    return redirect_url
