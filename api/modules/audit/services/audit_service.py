import json
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from config import AUDIT_LOG_FILE
from modules.audit.models import AuditEvent


SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "jwt",
    "secret",
}


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        result = {}

        for key, item in value.items():
            if key.lower() in SENSITIVE_KEYS:
                result[key] = "[REDACTED]"
            else:
                result[key] = _sanitize(item)

        return result

    if isinstance(value, list):
        return [_sanitize(item) for item in value]

    return value


def write_audit_log(
    *,
    db: Session,
    action: str,
    result: str,
    user_id: int | None = None,
    username: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_id: uuid.UUID | None = None,
    details: dict[str, Any] | None = None,
) -> AuditEvent:

    now = datetime.now(timezone.utc)
    event_uuid = uuid.uuid4()

    safe_details = _sanitize(details or {})

    event = AuditEvent(
        event_uuid=event_uuid,
        occurred_at=now,
        user_id=user_id,
        username=username,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        result=result,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
        details=safe_details,
        created_at=now,
    )

    db.add(event)
    db.flush()

    log_entry = {
        "event_uuid": str(event_uuid),
        "occurred_at": now.isoformat(),
        "user_id": user_id,
        "username": username,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "result": result,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "request_id": (
            str(request_id)
            if request_id
            else None
        ),
        "details": safe_details,
    }

    log_path = Path(AUDIT_LOG_FILE)
    log_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with log_path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                log_entry,
                ensure_ascii=False,
                default=str,
            )
            + "\n"
        )

    return event
