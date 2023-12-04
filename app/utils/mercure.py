import json
import urllib

import jwt
import requests
from django.conf import settings

# Helper functions for publishing events, generating JWT tokens, and generating the Hub URL.


def publish_event(topic="mytopicname", value="value"):
    """
    Publishes an event to the Mercure Hub.
    event_type: The type of the event, can be any string
    topic: The topic the event will be sent to. Only subscribers who request this topic will get notified.
    targets: The targets that are eligible to get the event.
    """

    token = get_jwt_token([], [])
    # token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJtZXJjdXJlIjp7InN1YnNjcmliZSI6WyJteXRvcGljbmFtZSJdLCJwdWJsaXNoIjpbIm15dG9waWNuYW1lIl19fQ.k0kjyeyOP2Sw9YC8KbaMgumX1jxptAh7dLoznpSpymY"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "topic": topic,
        "data": json.dumps({"key": value}),
    }

    response = requests.post(
        f"{settings.MERCURE_HUB_URL}/.well-known/mercure",
        data=data,
        headers=headers,
    )
    print(response.status_code)
    print(response.text)


def get_jwt_token(subscribe_targets=[], publish_targets=[]):
    """
    Creates a Mercure JWT token with the subscribe and publish targets.
    The JWT token gets signed with a key shared with the Mercure Hub.
    """
    return jwt.encode(
        {
            "mercure": {
                "subscribe": ["mytopicname"],
                "publish": ["mytopicname"],
            }
        },
        settings.MERCURE_PUBLISHER_JWT_KEY,
        algorithm="HS256",
    )


def get_hub_url(topics):
    """
    Returns the URL used to subscribe to the given topics in Mercure. The response
    will be an event stream.
    """
    params = [("topic", t) for t in topics]
    return settings.MERCURE_HUB_URL + "?" + urllib.parse.urlencode(params)
