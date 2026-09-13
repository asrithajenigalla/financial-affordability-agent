import os
import calendar

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any

from dotenv import load_dotenv

from models import (
    UserProfile,
    PaymentRequest,
    FinancialAgentOutput,
    PaymentPlan,
    PaymentPlanInstallment,
    SpendingChange,
    AffordabilityStatus,
    PaymentMethod
)

from exchange_rates import convert_currency


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)


# ============================================================
# MONEY
# ============================================================

CENT = Decimal("0.01")


def money(value) -> Decimal:

    return Decimal(str(value)).quantize(
        CENT,
        rounding=ROUND_HALF_UP
    )


# ============================================================
# DATE HELPERS
# ============================================================

def add_months(
    original_date: date,
    months: int
) -> date:

    year = original_date.year

    month = (
        original_date.month + months
    )

    while month > 12:

        month -= 12
        year += 1

    day = min(
        original_date.day,
        calendar.monthrange(
            year,
            month
        )[1]
    )

    return date(
        year,
        month,
        day
    )


# ============================================================
# EMPTY PAYMENT PLAN
# ============================================================

def empty_payment_plan() -> PaymentPlan:

    return PaymentPlan(
        is_applicable=False,
        number_of_installments=None,
        installments=[],
        total_plan_amount=None
    )


# ============================================================
# PAYMENT PLAN
# ============================================================

def build_installment_plan(
    safe_amount: Decimal,
    requested_amount: Decimal,
    desired_date: date,
    max_months: int | None
) -> PaymentPlan:

    safe_amount = money(safe_amount)

    requested_amount = money(
        requested_amount
    )

    remaining = money(
        requested_amount - safe_amount
    )

    if remaining <= Decimal("0.00"):

        return empty_payment_plan()

    if max_months is None:

        max_months = 1

    # We need at least two payments:
    # first safe payment + remaining amount.

    if max_months < 2:

        return empty_payment_plan()

    first_payment = safe_amount

    second_payment = remaining

    installments = [

        PaymentPlanInstallment(
            due_date=desired_date,
            amount=money(first_payment)
        ),

        PaymentPlanInstallment(
            due_date=add_months(
                desired_date,
                1
            ),
            amount=money(second_payment)
        )
    ]

    return PaymentPlan(

        is_applicable=True,

        number_of_installments=2,

        installments=installments,

        total_plan_amount=money(
            first_payment +
            second_payment
        )
    )


# ============================================================
# DETERMINISTIC DECISION
# ============================================================

def calculate_decision(
    user: UserProfile,
    request: PaymentRequest
) -> Dict[str, Any]:

    # --------------------------------------------------------
    # CURRENCIES
    # --------------------------------------------------------

    home_currency = (
        user.home_currency.upper()
    )

    request_currency = (
        request.request_currency.upper()
    )

    # --------------------------------------------------------
    # REQUESTED AMOUNT
    # --------------------------------------------------------

    requested_amount = money(
        request.requested_amount
    )

    # --------------------------------------------------------
    # TARGET DATE
    # --------------------------------------------------------

    target_date = (
        request.desired_completion_date
        or date.today()
    )

    # --------------------------------------------------------
    # CURRENCY CONVERSION
    # --------------------------------------------------------

    if request_currency != home_currency:

        converted_amount, rate, method = (
            convert_currency(
                requested_amount,
                request_currency,
                home_currency,
                target_date.isoformat()
            )
        )

        requested_amount = money(
            converted_amount
        )

    # --------------------------------------------------------
    # BALANCE
    # --------------------------------------------------------

    available_balance = money(
        user.current_available_balance
    )

    minimum_balance = money(
        user.minimum_balance_to_keep
    )

    # --------------------------------------------------------
    # SAFE SPENDING LIMIT
    # --------------------------------------------------------

    safe_amount = money(
        max(
            Decimal("0.00"),
            available_balance -
            minimum_balance
        )
    )

    # ========================================================
    # CASE 1: FULLY AFFORDABLE
    # ========================================================

    if requested_amount <= safe_amount:

        remaining_balance = money(
            available_balance -
            requested_amount
        )

        return {

            "amount_safe_to_pay":
                safe_amount,

            "affordability_status":
                AffordabilityStatus.AFFORDABLE,

            "recommended_payment_method":
                PaymentMethod.FULL_BALANCE,

            "payment_plan":
                empty_payment_plan(),

            "earliest_date_for_full_payment":
                None,

            "spending_changes_needed":
                [],

            "requested_amount":
                requested_amount,

            "available_balance":
                available_balance,

            "minimum_balance":
                minimum_balance,

            "remaining_balance":
                remaining_balance,

            "request_currency":
                request_currency,

            "home_currency":
                home_currency
        }

    # ========================================================
    # CASE 2: NOTHING SAFE TO PAY
    # ========================================================

    if safe_amount <= Decimal("0.00"):

        return {

            "amount_safe_to_pay":
                Decimal("0.00"),

            "affordability_status":
                AffordabilityStatus.NOT_AFFORDABLE,

            "recommended_payment_method":
                PaymentMethod.DEFER,

            "payment_plan":
                empty_payment_plan(),

            "earliest_date_for_full_payment":
                None,

            "spending_changes_needed":
                [],

            "requested_amount":
                requested_amount,

            "available_balance":
                available_balance,

            "minimum_balance":
                minimum_balance,

            "remaining_balance":
                available_balance,

            "request_currency":
                request_currency,

            "home_currency":
                home_currency
        }

    # ========================================================
    # CASE 3: PARTIALLY AFFORDABLE
    # ========================================================

    payment_plan = build_installment_plan(

        safe_amount=safe_amount,

        requested_amount=requested_amount,

        desired_date=target_date,

        max_months=user.max_installment_months
    )

    if payment_plan.is_applicable:

        payment_method = (
            PaymentMethod.AUTOPAY_MINIMUM
        )

    else:

        payment_method = (
            PaymentMethod.DEFER
        )

    return {

        "amount_safe_to_pay":
            safe_amount,

        "affordability_status":
            AffordabilityStatus.AFFORDABLE_WITH_ADJUSTMENTS,

        "recommended_payment_method":
            payment_method,

        "payment_plan":
            payment_plan,

        "earliest_date_for_full_payment":
            None,

        "spending_changes_needed":
            [],

        "requested_amount":
            requested_amount,

        "available_balance":
            available_balance,

        "minimum_balance":
            minimum_balance,

        "remaining_balance":
            money(
                available_balance -
                safe_amount
            ),

        "request_currency":
            request_currency,

        "home_currency":
            home_currency
    }


# ============================================================
# FALLBACK EXPLANATION
# ============================================================

def build_fallback_explanation(
    decision: Dict[str, Any],
    request: PaymentRequest
) -> str:

    requested = decision[
        "requested_amount"
    ]

    safe = decision[
        "amount_safe_to_pay"
    ]

    balance = decision[
        "available_balance"
    ]

    minimum = decision[
        "minimum_balance"
    ]

    currency = decision[
        "home_currency"
    ]

    status = decision[
        "affordability_status"
    ]

    plan = decision[
        "payment_plan"
    ]

    # --------------------------------------------------------
    # FULLY AFFORDABLE
    # --------------------------------------------------------

    if status == (
        AffordabilityStatus.AFFORDABLE
    ):

        remaining = decision[
            "remaining_balance"
        ]

        return (
            f'Your request to purchase '
            f'"{request.request_text}" for '
            f'{currency} {requested:.2f} '
            f'is affordable.\n\n'

            f'Available balance: '
            f'{currency} {balance:.2f}.\n'

            f'Protected minimum balance: '
            f'{currency} {minimum:.2f}.\n'

            f'Safe spending capacity: '
            f'{currency} {safe:.2f}.\n\n'

            f'You can pay the full amount '
            f'of {currency} {requested:.2f} '
            f'without going below the protected '
            f'minimum balance.\n\n'

            f'Estimated balance after payment: '
            f'{currency} {remaining:.2f}.'
        )

    # --------------------------------------------------------
    # PARTIALLY AFFORDABLE
    # --------------------------------------------------------

    if status == (
        AffordabilityStatus
        .AFFORDABLE_WITH_ADJUSTMENTS
    ):

        remaining = money(
            requested - safe
        )

        text = (
            f'Your request for '
            f'{currency} {requested:.2f} '
            f'is not fully affordable as a '
            f'single upfront payment.\n\n'

            f'Available balance: '
            f'{currency} {balance:.2f}.\n'

            f'Protected minimum balance: '
            f'{currency} {minimum:.2f}.\n'

            f'Maximum safe amount available now: '
            f'{currency} {safe:.2f}.\n\n'
        )

        if plan.is_applicable:

            text += (
                'A payment plan can cover the '
                'requested amount while keeping '
                'the protected minimum balance '
                'intact.\n\n'
                'Recommended payment plan:'
            )

            for index, installment in enumerate(
                plan.installments,
                start=1
            ):

                text += (
                    f'\n{index}. '
                    f'{currency} '
                    f'{installment.amount:.2f} '
                    f'on '
                    f'{installment.due_date.isoformat()}'
                )

            text += (
                f'\n\nTotal planned amount: '
                f'{currency} '
                f'{plan.total_plan_amount:.2f}.'
            )

        else:

            text += (
                f'The remaining amount of '
                f'{currency} {remaining:.2f} '
                f'cannot currently be covered '
                f'safely under the configured '
                f'payment options.'
            )

        return text

    # --------------------------------------------------------
    # NOT AFFORDABLE
    # --------------------------------------------------------

    return (
        f'Your request for '
        f'{currency} {requested:.2f} '
        f'is currently not affordable '
        f'under the available financial '
        f'constraints.\n\n'

        f'Available balance: '
        f'{currency} {balance:.2f}.\n'

        f'Protected minimum balance: '
        f'{currency} {minimum:.2f}.\n\n'

        f'No amount can safely be paid '
        f'without reducing the balance '
        f'below the protected minimum. '
        f'The recommended action is '
        f'to defer the payment.'
    )


# ============================================================
# GEMINI
# ============================================================

def generate_gemini_explanation(
    decision: Dict[str, Any],
    request: PaymentRequest
) -> str:

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    plan = decision[
        "payment_plan"
    ]

    installments = []

    for item in plan.installments:

        installments.append({
            "due_date":
                item.due_date.isoformat(),

            "amount":
                f"{item.amount:.2f}"
        })

    decision_for_ai = {

        "requested_amount":
            f"{decision['requested_amount']:.2f}",

        "available_balance":
            f"{decision['available_balance']:.2f}",

        "minimum_balance":
            f"{decision['minimum_balance']:.2f}",

        "amount_safe_to_pay":
            f"{decision['amount_safe_to_pay']:.2f}",

        "remaining_balance":
            f"{decision['remaining_balance']:.2f}",

        "home_currency":
            decision["home_currency"],

        "affordability_status":
            decision[
                "affordability_status"
            ].value,

        "recommended_payment_method":
            decision[
                "recommended_payment_method"
            ].value,

        "payment_plan": {

            "is_applicable":
                plan.is_applicable,

            "number_of_installments":
                plan.number_of_installments,

            "installments":
                installments,

            "total_plan_amount":
                (
                    f"{plan.total_plan_amount:.2f}"
                    if plan.total_plan_amount
                    is not None
                    else None
                )
        }
    }

    prompt = f"""
You are the explanation component of a
Financial Affordability Agent.

The financial decision below has already been
calculated by deterministic Python code.

You MUST NOT:
- recalculate financial amounts
- modify financial amounts
- change the affordability status
- change the payment method
- create a different payment plan
- invent income
- invent expenses
- invent spending cuts
- provide investment advice
- provide medical advice

Use ONLY the supplied deterministic decision.

Explain:
1. What the user wants to purchase.
2. The requested amount.
3. Available balance.
4. Protected minimum balance.
5. Safe amount.
6. Affordability status.
7. Recommended payment method.
8. Payment plan if applicable.
9. Why the decision was made.

Do not claim future income.
Do not invent financial information.
Do not claim that an installment plan makes
the purchase immediately affordable.

Keep the explanation concise and professional.

USER REQUEST:
{request.request_text}

DETERMINISTIC DECISION:
{decision_for_ai}
"""

    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=700
        )
    )

    text = getattr(
        response,
        "text",
        None
    )

    if not text or not text.strip():

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return text.strip()


# ============================================================
# FINAL AGENT
# ============================================================

def financial_agent(
    user: UserProfile,
    request: PaymentRequest
) -> FinancialAgentOutput:

    # --------------------------------------------------------
    # STEP 1
    # Deterministic financial calculation
    # --------------------------------------------------------

    decision = calculate_decision(
        user,
        request
    )

    # --------------------------------------------------------
    # STEP 2
    # Gemini explanation
    # --------------------------------------------------------

    try:

        explanation = (
            generate_gemini_explanation(
                decision,
                request
            )
        )

    except Exception as exc:

        print(
            f"Gemini unavailable: {exc}"
        )

        explanation = (
            build_fallback_explanation(
                decision,
                request
            )
        )

    # --------------------------------------------------------
    # STEP 3
    # Final validated response
    # --------------------------------------------------------

    return FinancialAgentOutput(

        amount_safe_to_pay=money(
            decision[
                "amount_safe_to_pay"
            ]
        ),

        affordability_status=
            decision[
                "affordability_status"
            ],

        recommended_payment_method=
            decision[
                "recommended_payment_method"
            ],

        payment_plan=
            decision[
                "payment_plan"
            ],

        earliest_date_for_full_payment=
            decision[
                "earliest_date_for_full_payment"
            ],

        spending_changes_needed=
            decision[
                "spending_changes_needed"
            ],

        decision_explanation=
            explanation
    )