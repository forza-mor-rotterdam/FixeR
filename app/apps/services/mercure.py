import json
import logging

import jwt
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class MercurePublisher:
    _subscribe_targets = ["*"]
    _publish_targets = ["/taak/{id}/"]
    _mercure_url = None
    _mercure_publisher_jwt_key = None

    def __init__(self):
        logger.info(f"MercurePublisher public url: {settings.APP_MERCURE_PUBLIC_URL}")
        logger.info(
            f"MercurePublisher internal url: {settings.APP_MERCURE_INTERNAL_URL}"
        )
        self._mercure_url = settings.APP_MERCURE_INTERNAL_URL
        logger.info(f"MercurePublisher _mercure_url: {self._mercure_url}")
        self._mercure_publisher_jwt_key = settings.MERCURE_PUBLISHER_JWT_KEY

    def _get_jwt_token(self):
        return jwt.encode(
            {
                "mercure": {
                    "subscribe": self._subscribe_targets,
                    "publish": self._publish_targets,
                }
            },
            self._mercure_publisher_jwt_key,
            algorithm="HS256",
        )

    def publish(self, topic: str, data: dict = {}):
        logger.info(f"Publish with topic: {topic}")
        logger.info(f"Publish with data: {data}")
        token = self._get_jwt_token()
        logger.info(f"Publish with token: {token}")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "topic": topic,
            "data": json.dumps(data),
        }

        response = requests.post(
            self._mercure_url,
            data=data,
            headers=headers,
        )
        logger.info(f"Publish response status_code: {response.status_code}")
        logger.info(f"Publish response text: {response.text}")
