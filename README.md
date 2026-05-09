# FastAPI + Sentry (demo)

Prosta aplikacja FastAPI z endpointami, które celowo generują błędy i wysyłają je do Sentry.

## 1. Instalacja

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Konfiguracja Sentry

1. Skopiuj plik konfiguracyjny:

```bash
cp .env.example .env
```

2. Ustaw własny `SENTRY_DSN` w `.env`.
3. Aplikacja ładuje `.env` automatycznie przy starcie.

## 3. Uruchomienie

```bash
uvicorn main:app --reload
```

Dokumentacja Swagger: `http://127.0.0.1:8000/docs`

## 4. Endpointy

- `GET /` — prosty endpoint kontrolny.
- `GET /health` — status aplikacji.
- `GET /error/divide-by-zero` — wymusza `ZeroDivisionError` (500, przechwytywany przez Sentry).
- `GET /error/value` — wymusza `ValueError` (500, przechwytywany przez Sentry).
- `GET /error/http` — przechwytuje wyjątek ręcznie (`capture_exception`) i zwraca `HTTP 500`.
- `GET /sentry/message` — wysyła testową wiadomość do Sentry (`capture_message`).
- `GET /api/orders/{order_id}/details` — realistyczny błąd: dla nieistniejącego ID rzuca wyjątek typu `NoneType`.
- `POST /api/invoices/create` — realistyczny błąd: podwójne parsowanie JSON (`json.loads`), np. body `{ "metadata": { "source": "web" } }`.

## Uwaga

Jeśli `SENTRY_DSN` nie jest ustawiony, aplikacja działa normalnie, ale nie wysyła eventów do Sentry.
