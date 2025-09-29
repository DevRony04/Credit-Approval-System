from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple

from .models import Customer, Loan

LAKH = Decimal("100000")


def calculate_approved_limit(monthly_income: Decimal) -> Decimal:
    base = Decimal(36) * Decimal(monthly_income)
    # Round to nearest lakh
    return (base / LAKH).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * LAKH


def amortized_monthly_payment(principal: Decimal, annual_rate_percent: Decimal, months: int) -> Decimal:
    if months <= 0:
        return Decimal("0")
    monthly_rate = (Decimal(annual_rate_percent) / Decimal(100)) / Decimal(12)
    if monthly_rate == 0:
        return (Decimal(principal) / Decimal(months)).quantize(Decimal("0.01"))
    r = monthly_rate
    n = Decimal(months)
    numerator = r * (1 + r) ** n
    denominator = (1 + r) ** n - 1
    payment = Decimal(principal) * numerator / denominator
    return payment.quantize(Decimal("0.01"))


def compute_credit_score(customer: Customer) -> int:
    loans = list(customer.loans.all())
    total_active_amount = sum((l.loan_amount for l in loans), Decimal("0"))
    if total_active_amount > customer.approved_limit:
        return 0

    score = 0
    # On-time EMI ratio (40)
    total_emis = sum((l.tenure for l in loans), 0)
    on_time = sum((l.emis_paid_on_time for l in loans), 0)
    ratio = (on_time / total_emis) if total_emis > 0 else 1
    score += int(ratio * 40)

    # Number of loans (20) - fewer loans is better
    num_loans = len(loans)
    score += max(0, 20 - min(num_loans, 10) * 2)

    # Loan activity in current year (20)
    current_year = date.today().year
    has_activity = any(l.start_date.year == current_year or l.end_date.year == current_year for l in loans)
    score += 20 if has_activity else 10

    # Loan volume vs approved_limit (20)
    volume_ratio = (total_active_amount / customer.approved_limit) if customer.approved_limit > 0 else Decimal("0")
    score += max(0, int((1 - min(volume_ratio, 1)) * 20))

    return max(0, min(100, score))


def check_eligibility(customer: Customer, loan_amount: Decimal, interest_rate: Decimal, tenure: int) -> Tuple[bool, Decimal, int, str]:
    credit_score = compute_credit_score(customer)
    proposed_emi = amortized_monthly_payment(Decimal(loan_amount), Decimal(interest_rate), tenure)

    # If total EMIs > 50% of income -> reject
    current_emis = sum((amortized_monthly_payment(l.loan_amount, l.interest_rate, l.tenure) for l in customer.loans.all()), Decimal("0"))
    income_threshold = Decimal(customer.monthly_income) * Decimal("0.5")
    if current_emis + proposed_emi > income_threshold:
        return False, Decimal(interest_rate), credit_score, "EMI exceeds 50% income"

    corrected_rate = Decimal(interest_rate)
    if credit_score > 50:
        pass
    elif 30 < credit_score <= 50:
        if corrected_rate <= Decimal("12"):
            corrected_rate = Decimal("12")
    elif 10 < credit_score <= 30:
        if corrected_rate <= Decimal("16"):
            corrected_rate = Decimal("16")
    else:
        return False, corrected_rate, credit_score, "Credit score too low"

    return True, corrected_rate, credit_score, "Eligible"
