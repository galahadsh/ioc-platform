import json
import os

import redis
from redis.exceptions import (
    ConnectionError,
    TimeoutError,
)


class DocumentQueue:
    def __init__(self) -> None:
        redis_url = os.getenv(
            "REDIS_URL",
        )

        if not redis_url:
            raise RuntimeError(
                "REDIS_URL no está configurado."
            )

        self.client = redis.Redis.from_url(
            redis_url,
            decode_responses=True,

            # Debe ser mayor que el timeout
            # utilizado por BLPOP.
            socket_timeout=15,

            socket_connect_timeout=5,

            health_check_interval=30,

            retry_on_timeout=True,
        )

        self.queue_name = (
            "cip:documents:processing"
        )

    def ping(self) -> bool:
        try:
            return bool(
                self.client.ping()
            )

        except (
            ConnectionError,
            TimeoutError,
        ):
            return False

    def enqueue(
        self,
        document_id: int,
    ) -> None:
        payload = {
            "document_id": int(
                document_id
            ),
        }

        self.client.rpush(
            self.queue_name,
            json.dumps(
                payload
            ),
        )

    def dequeue(
        self,
        timeout: int = 5,
    ) -> dict | None:
        try:
            result = self.client.blpop(
                self.queue_name,
                timeout=timeout,
            )

        except TimeoutError:
            # No debe matar al worker.
            # Simplemente continuamos
            # esperando trabajo.
            return None

        except ConnectionError as error:
            raise RuntimeError(
                "Se perdió la conexión "
                "con Redis."
            ) from error

        if result is None:
            return None

        _, payload = result

        return json.loads(
            payload
        )

    def size(self) -> int:
        return int(
            self.client.llen(
                self.queue_name
            )
        )
