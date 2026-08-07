import os
from datetime import timedelta
from io import BytesIO

from minio import Minio
from minio.error import S3Error


class StorageService:
    def __init__(self) -> None:
        endpoint = os.getenv(
            "MINIO_ENDPOINT",
            "minio:9000",
        )

        access_key = os.getenv(
            "MINIO_ACCESS_KEY"
        )

        secret_key = os.getenv(
            "MINIO_SECRET_KEY"
        )

        bucket = os.getenv(
            "MINIO_BUCKET",
            "cyber-intelligence-documents",
        )

        secure = (
            os.getenv(
                "MINIO_SECURE",
                "false",
            ).lower()
            == "true"
        )

        if not access_key:
            raise RuntimeError(
                "MINIO_ACCESS_KEY no está configurado."
            )

        if not secret_key:
            raise RuntimeError(
                "MINIO_SECRET_KEY no está configurado."
            )

        self.bucket = bucket

        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def ensure_bucket(self) -> None:
        if not self.client.bucket_exists(
            self.bucket
        ):
            self.client.make_bucket(
                self.bucket
            )

    def upload_bytes(
        self,
        *,
        object_name: str,
        data: bytes,
        content_type: str = (
            "application/octet-stream"
        ),
    ) -> dict:
        self.ensure_bucket()

        stream = BytesIO(data)

        result = self.client.put_object(
            self.bucket,
            object_name,
            stream,
            length=len(data),
            content_type=content_type,
        )

        return {
            "bucket": self.bucket,
            "object_name": object_name,
            "etag": result.etag,
            "version_id": (
                result.version_id
            ),
            "size": len(data),
            "content_type": content_type,
        }

    def download_bytes(
        self,
        object_name: str,
    ) -> bytes:
        response = None

        try:
            response = (
                self.client.get_object(
                    self.bucket,
                    object_name,
                )
            )

            return response.read()

        finally:
            if response is not None:
                response.close()
                response.release_conn()

    def exists(
        self,
        object_name: str,
    ) -> bool:
        try:
            self.client.stat_object(
                self.bucket,
                object_name,
            )

            return True

        except S3Error as error:
            if error.code in {
                "NoSuchKey",
                "NoSuchObject",
                "NoSuchBucket",
            }:
                return False

            raise

    def delete(
        self,
        object_name: str,
    ) -> None:
        self.client.remove_object(
            self.bucket,
            object_name,
        )

    def presigned_download_url(
        self,
        object_name: str,
        *,
        expires_minutes: int = 15,
    ) -> str:
        return (
            self.client.presigned_get_object(
                self.bucket,
                object_name,
                expires=timedelta(
                    minutes=expires_minutes
                ),
            )
        )
