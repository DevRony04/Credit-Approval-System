from __future__ import annotations

import uuid
from django.db import models


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    phone_number = models.CharField(max_length=20, unique=True)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=12, decimal_places=2)
    current_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self) -> str:  # pragma: no cover - admin/debug
        return f"{self.first_name} {self.last_name}"


class Loan(models.Model):
    loan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.PositiveIntegerField(help_text="Tenure in months")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual interest rate %")
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2)
    emis_paid_on_time = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self) -> str:  # pragma: no cover
        return f"Loan {self.loan_id} for {self.customer_id}"
