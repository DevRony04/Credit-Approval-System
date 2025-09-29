# Credit Approval System

Django + DRF + Celery + Redis + PostgreSQL, fully dockerized.

## Quick start

1. Create data files in `./data/`:
   - `customer_data.xlsx`
   - `loan_data.xlsx`

2. Start stack:

```bash
docker compose up --build
```

This launches:
- web (Django + Gunicorn + Uvicorn worker)
- worker (Celery)
- beat (Celery Beat)
- db (PostgreSQL)
- redis (Redis)

The app listens on `http://localhost:8000`.

## Environment
See `.env` for defaults. Update DB credentials if needed.

## API Endpoints

- POST `/register`
- POST `/check-eligibility`
- POST `/create-loan`
- GET `/view-loan/<loan_id>`
- GET `/view-loans/<customer_id>`

### Examples

Register:
```bash
curl -X POST http://localhost:8000/register \
  -H 'Content-Type: application/json' \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "phone_number": "+15550001",
    "monthly_income": 85000
  }'
```

Check eligibility:
```bash
curl -X POST http://localhost:8000/check-eligibility \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_id": 1,
    "loan_amount": 500000,
    "interest_rate": 10,
    "tenure": 24
  }'
```

Create loan:
```bash
curl -X POST http://localhost:8000/create-loan \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_id": 1,
    "loan_amount": 500000,
    "interest_rate": 10,
    "tenure": 24
  }'
```

View loan:
```bash
curl http://localhost:8000/view-loan/<loan_uuid>
```

View loans for customer:
```bash
curl http://localhost:8000/view-loans/1
```

## Data ingestion
- Celery task `ingest_excel_data` ingests from `./data/customer_data.xlsx` and `./data/loan_data.xlsx`.
- On container startup, `entrypoint.sh` runs `python manage.py ingest_data`.

## Development (without Docker)
```bash
python -m venv .venv && . .venv/bin/activate  # on Windows use .venv\\Scripts\\activate
pip install -r requirements.txt
export DJANGO_DEBUG=True
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
