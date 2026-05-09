import os
import json
from pathlib import Path
from typing import Any

import sentry_sdk
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from sentry_sdk.integrations.fastapi import FastApiIntegration

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SENTRY_DSN = os.getenv("SENTRY_DSN")
ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "local")
RELEASE = os.getenv("SENTRY_RELEASE", "sentry-research@0.1.0")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FastApiIntegration()],
        environment=ENVIRONMENT,
        release=RELEASE,
        traces_sample_rate=1.0,
        send_default_pii=False,
    )

app = FastAPI(title="FastAPI + Sentry demo")


class InvoiceCreatePayload(BaseModel):
    metadata: Any


FAKE_ORDERS_DB: dict[str, dict[str, Any]] = {
    "known-order": {
        "id": "known-order",
        "customer": {"email": "anna@example.com"},
    }
}

FAKE_USERS: list[dict[str, Any]] = []


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "FastAPI działa"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/error/divide-by-zero")
def error_divide_by_zero() -> dict[str, float]:
    result = 1 / 0
    return {"result": result}


@app.get("/error/value")
def error_value() -> None:
    raise ValueError("To jest testowy błąd ValueError wysyłany do Sentry")


@app.get("/error/http")
def error_http() -> None:
    try:
        raise RuntimeError("To jest testowy błąd RuntimeError")
    except RuntimeError as exc:
        sentry_sdk.capture_exception(exc)
    raise HTTPException(status_code=500, detail="Błąd testowy zgłoszony do Sentry")


@app.get("/sentry/message")
def sentry_message() -> dict[str, str]:
    sentry_sdk.capture_message("Testowa wiadomość z endpointu /sentry/message")
    return {"status": "message_sent"}


@app.get("/api/orders/{order_id}/details")
def order_details(order_id: str) -> dict[str, str]:
    order = FAKE_ORDERS_DB.get(order_id)

    customer_email = order["customer"]["email"]

    return {"order_id": order["id"], "customer_email": customer_email}


@app.post("/api/invoices/create")
def create_invoice(payload: InvoiceCreatePayload) -> dict[str, Any]:
    metadata = json.loads(payload.metadata)

    return {
        "id": f"inv-{os.urandom(4).hex()}",
        "metadata": metadata,
    }


@app.get("/api/users/stats")
def users_stats() -> dict[str, float | int]:
    active_users = [user for user in FAKE_USERS if user.get("is_active")]
    average_age = sum(user["age"] for user in active_users) / len(active_users)

    return {
        "active_users_count": len(active_users),
        "average_age": average_age,
    }


@app.get("/sentry-debug")
async def trigger_error() -> None:
    division_by_zero = 1 / 0
