from datetime import datetime
from dateutil.relativedelta import relativedelta


def calculate_safe_amount(user, requested_amount):

    available_after_minimum = (
        user.current_available_balance
        - user.minimum_balance_to_keep
    )

    if available_after_minimum <= 0:
        return 0.0

    return min(
        requested_amount,
        available_after_minimum
    )


def determine_status(
    requested_amount,
    safe_amount,
    user
):

    if requested_amount <= 0:
        return "insufficient_data"

    if safe_amount >= requested_amount:
        return "affordable"

    if safe_amount > 0:
        return "affordable_with_adjustments"

    return "not_affordable"


def choose_payment_method(
    user,
    status,
    safe_amount,
    requested_amount
):

    methods = user.payment_methods_user_will_consider

    if status == "affordable":

        if "full_payment" in methods:
            return "full_balance"

    if (
        "partial_payment" in methods
        and safe_amount > 0
    ):
        return "autopay_minimum"

    if "installments" in methods:

        if user.max_installment_months:
            return "installments"

    if "full_payment" in methods:
        return "full_balance"

    return "defer"


def create_installment_plan(
    amount,
    months
):

    if not months or months <= 0:
        return None

    monthly_amount = amount / months

    installments = []

    start_date = datetime(2026, 10, 1)

    for i in range(months):

        due_date = start_date + relativedelta(
            months=i
        )

        installments.append({
            "due_date": due_date.strftime("%Y-%m-%d"),
            "amount": f"{monthly_amount:.2f}"
        })

    return {
        "is_applicable": True,
        "number_of_installments": months,
        "installments": installments,
        "total_plan_amount": f"{amount:.2f}"
    }