from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Customer, Loan
from .serializers import (
    CustomerSerializer,
    RegisterCustomerSerializer,
    CheckEligibilitySerializer,
    CreateLoanSerializer,
    LoanSerializer,
)
from .services import calculate_approved_limit, amortized_monthly_payment, check_eligibility


@api_view(["POST"])
def register(request):
    serializer = RegisterCustomerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    approved_limit = calculate_approved_limit(data["monthly_income"])
    customer = Customer.objects.create(
        first_name=data["first_name"],
        last_name=data["last_name"],
        age=data["age"],
        phone_number=data["phone_number"],
        monthly_income=data["monthly_income"],
        approved_limit=approved_limit,
        current_debt=Decimal("0"),
    )
    return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def check_eligibility_view(request):
    serializer = CheckEligibilitySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    customer = get_object_or_404(Customer, pk=data["customer_id"])

    eligible, corrected_rate, credit_score, message = check_eligibility(
        customer,
        data["loan_amount"],
        data["interest_rate"],
        data["tenure"],
    )
    monthly_installment = amortized_monthly_payment(data["loan_amount"], corrected_rate, data["tenure"])

    return Response(
        {
            "eligible": eligible,
            "credit_score": credit_score,
            "corrected_interest_rate": str(corrected_rate),
            "monthly_installment": str(monthly_installment),
            "message": message,
        }
    )


@api_view(["POST"])
def create_loan(request):
    serializer = CreateLoanSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    customer = get_object_or_404(Customer, pk=data["customer_id"])

    eligible, corrected_rate, credit_score, message = check_eligibility(
        customer,
        data["loan_amount"],
        data["interest_rate"],
        data["tenure"],
    )
    if not eligible:
        return Response({"eligible": False, "message": message, "credit_score": credit_score}, status=status.HTTP_400_BAD_REQUEST)

    start_date = date.today()
    end_date = start_date + timedelta(days=30 * data["tenure"])  # approx months
    monthly_installment = amortized_monthly_payment(data["loan_amount"], corrected_rate, data["tenure"])

    loan = Loan.objects.create(
        customer=customer,
        loan_amount=data["loan_amount"],
        tenure=data["tenure"],
        interest_rate=corrected_rate,
        monthly_repayment=monthly_installment,
        emis_paid_on_time=0,
        start_date=start_date,
        end_date=end_date,
    )

    return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def view_loan(request, loan_id: str):
    loan = get_object_or_404(Loan, pk=loan_id)
    return Response(LoanSerializer(loan).data)


@api_view(["GET"])
def view_loans(request, customer_id: int):
    customer = get_object_or_404(Customer, pk=customer_id)
    loans = customer.loans.all()
    return Response(LoanSerializer(loans, many=True).data)
