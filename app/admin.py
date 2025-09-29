from __future__ import annotations

from django.contrib import admin
from .models import Customer, Loan


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "phone_number", "monthly_income", "approved_limit", "current_debt")
    search_fields = ("first_name", "last_name", "phone_number")


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("loan_id", "customer", "loan_amount", "tenure", "interest_rate", "monthly_repayment", "emis_paid_on_time", "start_date", "end_date")
    list_filter = ("start_date", "end_date")
    search_fields = ("loan_id",)
