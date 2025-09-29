from __future__ import annotations

from rest_framework import serializers
from .models import Customer, Loan


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "age",
            "phone_number",
            "monthly_income",
            "approved_limit",
            "current_debt",
        ]
        read_only_fields = ["approved_limit", "current_debt", "id"]


class RegisterCustomerSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField(min_value=18, max_value=120)
    phone_number = serializers.CharField(max_length=20)
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2)


class CheckEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField(min_value=1)


class CreateLoanSerializer(CheckEligibilitySerializer):
    pass


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            "loan_id",
            "customer",
            "loan_amount",
            "tenure",
            "interest_rate",
            "monthly_repayment",
            "emis_paid_on_time",
            "start_date",
            "end_date",
        ]
