from __future__ import annotations

from decimal import Decimal
from datetime import datetime, timedelta
from celery import shared_task
from django.conf import settings
import pandas as pd

from .models import Customer, Loan
from .services import calculate_approved_limit, amortized_monthly_payment


@shared_task
def ingest_excel_data() -> int:
    created = 0
    data_dir = settings.DATA_DIR

    customer_file = data_dir / "customer_data.xlsx"
    if customer_file.exists():
        df = pd.read_excel(customer_file)
        for _, row in df.iterrows():
            customer, _ = Customer.objects.get_or_create(
                phone_number=str(row.get("phone_number")),
                defaults={
                    "first_name": row.get("first_name", ""),
                    "last_name": row.get("last_name", ""),
                    "age": int(row.get("age", 0)),
                    "monthly_income": Decimal(str(row.get("monthly_income", 0))),
                    "approved_limit": calculate_approved_limit(Decimal(str(row.get("monthly_income", 0)))),
                    "current_debt": Decimal(str(row.get("current_debt", 0))),
                },
            )
            if _:
                created += 1

    loan_file = data_dir / "loan_data.xlsx"
    if loan_file.exists():
        df = pd.read_excel(loan_file)
        for _, row in df.iterrows():
            try:
                customer = Customer.objects.get(phone_number=str(row.get("phone_number")))
            except Customer.DoesNotExist:
                continue
            tenure = int(row.get("tenure", 0))
            rate = Decimal(str(row.get("interest_rate", 0)))
            amount = Decimal(str(row.get("loan_amount", 0)))
            start = row.get("start_date")
            if isinstance(start, float):
                start = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(start) - 2).date()
            elif isinstance(start, pd.Timestamp):
                start = start.date()
            elif not start:
                start = datetime.utcnow().date()
            end = start + timedelta(days=30 * tenure)
            monthly = amortized_monthly_payment(amount, rate, tenure)
            Loan.objects.get_or_create(
                customer=customer,
                loan_amount=amount,
                tenure=tenure,
                interest_rate=rate,
                monthly_repayment=monthly,
                start_date=start,
                end_date=end,
                defaults={"emis_paid_on_time": int(row.get("emis_paid_on_time", 0))},
            )
    return created
