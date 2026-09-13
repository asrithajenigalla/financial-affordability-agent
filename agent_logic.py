"""
agent_logic.py

Rule-based implementation of run_agent(). Uses `type` (emergency_expense,
debt_repayment, investment, housing) as the primary driver of affordability
logic, with free-text parsing as a secondary signal. This is a heuristic
stand-in for a real affordability engine -- see the caveat at the bottom.
"""

import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional

from models import (
    AffordabilityStatus,
    FinancialAgentOutput,
    PaymentMethod,
    PaymentPlan,
    PaymentPlanInstallment,
    SpendingChange,
)

# ---- Request type constants ----------------------------------------------

TYPE_EMERGENCY = "emergency_expense"
TYPE_DEBT = "debt_repayment"
TYPE_INVESTMENT = "investment"
TYPE_HOUSING = "housing"
KNOWN_TYPES = {TYPE_EMERGENCY, TYPE_DEBT, TYPE_INVESTMENT, TYPE_HOUSING}

# Per-type base assumptions: what fraction of the requested amount is
# treated as "safe to pay now" absent any text signal, and whether the
# type structurally implies an installment plan. These are placeholder
# defaults -- replace with real underwriting rules per type when available.
TYPE_BASE_SAFE_FRACTION = {
    TYPE_EMERGENCY: Decimal("0.40"),   # urgent, but often large/unplanned
    TYPE_DEBT: Decimal("0.60"),        # usually recurring, budgeted-for
    TYPE_INVESTMENT: Decimal("0.50"),  # discretionary, should be conservative
    TYPE_HOUSING: Decimal("0.70"),     # typically recurring/expected (rent, mortgage)
}
TYPE_DEFAULT_INSTALLMENTS_PREFERRED = {
    TYPE_EMERGENCY: True,
    TYPE_DEBT: True,
    TYPE_INVESTMENT: False,
    TYPE_HOUSING: False,
}

# ---- Text signal patterns --------------------------------------------------

HARDSHIP_PATTERNS = [
    r"\blost my job\b", r"\blaid off\b", r"\bunemployed\b",
    r"\bmedical (bill|emergency|expense)\b", r"\bhospital\b",
    r"\bcan't afford\b", r"\bcannot afford\b", r"\bstruggling\b",
    r"\bbehind on\b", r"\bevict", r"\bshut ?off\b", r"\bfinancial hardship\b",
]
TIGHT_BUDGET_PATTERNS = [
    r"\btight (on|this) month\b", r"\bliving paycheck to paycheck\b",
    r"\bcash flow\b", r"\bpartial payment\b", r"\binstallment", r"\bsplit (the|this) payment\b",
    r"\bneed more time\b", r"\bextension\b",
]
STABLE_PATTERNS = [
    r"\bno problem\b", r"\bcan pay in full\b", r"\bhave the funds\b",
    r"\bjust confirming\b", r"\bpay(ing)? (it |this )?off (today|now|immediately)\b",
    r"\bsavings? (is|are) sufficient\b",
]
HIGH_RISK_INVESTMENT_PATTERNS = [
    r"\ball[- ]in\b", r"\bleverage\b", r"\bmargin\b", r"\bcrypto\b",
    r"\byolo\b", r"\bhigh[- ]risk\b", r"\bspeculative\b",
]

DISCRETIONARY_CATEGORY_HINTS = {
    "dining_out": [r"\beating out\b", r"\brestaurants?\b", r"\bdoordash\b", r"\buber ?eats\b"],
    "subscriptions": [r"\bsubscriptions?\b", r"\bstreaming\b", r"\bnetflix\b", r"\bspotify\b"],
    "entertainment": [r"\bentertainment\b", r"\bconcerts?\b", r"\bmovies?\b"],
    "shopping": [r"\bonline shopping\b", r"\bamazon\b", r"\bimpulse buy"],
}


def _search_any(patterns: list[str], text: str) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)


def _parse_amount(raw: str) -> Decimal:
    cleaned = re.sub(r"[^\d.]", "", raw or "")
    try:
        return Decimal(cleaned) if cleaned else Decimal("0")
    except InvalidOperation:
        return Decimal("0")


def _parse_date(raw: str) -> Optional[date]:
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _normalize_type(raw_type: str) -> str:
    normalized = (raw_type or "").strip().lower().replace(" ", "_").replace("-", "_")
    return normalized if normalized in KNOWN_TYPES else "unknown"


# ---- Core assessment -------------------------------------------------------

def _assess_affordability(
    request_type: str, requested_amount: Decimal, text: str
) -> tuple[AffordabilityStatus, Decimal, bool]:
    """
    Returns (status, amount_safe_to_pay, needs_installments).

    request_type sets the base safe-fraction and installment preference;
    text signals adjust that base up or down. Replace with real account
    data (balance, income, DTI) when available -- this is a heuristic
    placeholder keyed on type + keyword matching only.
    """
    base_fraction = TYPE_BASE_SAFE_FRACTION.get(request_type, Decimal("0.60"))
    prefers_installments = TYPE_DEFAULT_INSTALLMENTS_PREFERRED.get(request_type, True)

    if _search_any(HARDSHIP_PATTERNS, text):
        fraction = min(base_fraction, Decimal("0.25"))
        status = AffordabilityStatus.NOT_AFFORDABLE
        needs_installments = True

    elif request_type == TYPE_INVESTMENT and _search_any(HIGH_RISK_INVESTMENT_PATTERNS, text):
        # Investment-specific guardrail: speculative/high-risk language
        # caps the safe amount regardless of stated affordability, since
        # over-committing to discretionary risk is the harm being guarded
        # against here, not a cash-flow problem.
        fraction = min(base_fraction, Decimal("0.30"))
        status = AffordabilityStatus.AFFORDABLE_WITH_ADJUSTMENTS
        needs_installments = False

    elif _search_any(TIGHT_BUDGET_PATTERNS, text):
        fraction = min(base_fraction, Decimal("0.50"))
        status = AffordabilityStatus.AFFORDABLE_WITH_ADJUSTMENTS
        needs_installments = True

    elif _search_any(STABLE_PATTERNS, text):
        fraction = Decimal("1.0")
        status = AffordabilityStatus.AFFORDABLE
        needs_installments = False

    elif requested_amount <= 0:
        fraction = Decimal("0")
        status = AffordabilityStatus.INSUFFICIENT_DATA
        needs_installments = False

    else:
        # No strong text signal -- fall back to the type's base assumption.
        fraction = base_fraction
        status = (
            AffordabilityStatus.AFFORDABLE
            if fraction >= Decimal("0.95")
            else AffordabilityStatus.AFFORDABLE_WITH_ADJUSTMENTS
        )
        needs_installments = prefers_installments and requested_amount > Decimal("500")

    amount_safe_to_pay = (requested_amount * fraction).quantize(Decimal("0.01"))
    return status, amount_safe_to_pay, needs_installments


def _recommend_payment_method(
    request_type: str, status: AffordabilityStatus, needs_installments: bool
) -> PaymentMethod:
    if status == AffordabilityStatus.NOT_AFFORDABLE:
        return PaymentMethod.DEFER
    if status == AffordabilityStatus.INSUFFICIENT_DATA:
        return PaymentMethod.DEFER
    if status == AffordabilityStatus.AFFORDABLE and not needs_installments:
        return PaymentMethod.FULL_BALANCE
    if request_type == TYPE_DEBT and needs_installments:
        # Existing debt repayment -> autopay minimum is usually the
        # structurally appropriate default over ad hoc installments.
        return PaymentMethod.AUTOPAY_MINIMUM
    if needs_installments:
        return PaymentMethod.MANUAL_INSTALLMENTS
    return PaymentMethod.LINE_OF_CREDIT if request_type == TYPE_HOUSING else PaymentMethod.AUTOPAY_MINIMUM


def _build_payment_plan(
    total_amount: Decimal,
    amount_already_safe: Decimal,
    needs_installments: bool,
    desired_completion_date: Optional[date],
) -> PaymentPlan:
    remaining = (total_amount - amount_already_safe).quantize(Decimal("0.01"))

    if not needs_installments or remaining <= 0:
        return PaymentPlan(is_applicable=False)

    today = date.today()
    if desired_completion_date and desired_completion_date > today:
        months_available = max(
            1,
            (desired_completion_date.year - today.year) * 12
            + (desired_completion_date.month - today.month),
        )
        num_installments = max(2, min(6, months_available))
    else:
        num_installments = 3

    base_installment = (remaining / num_installments).quantize(Decimal("0.01"))
    installments = []
    running_total = Decimal("0.00")
    for i in range(num_installments):
        due = (today.replace(day=1) + timedelta(days=31 * (i + 1))).replace(day=1)
        amt = base_installment
        if i == num_installments - 1:
            amt = (remaining - running_total).quantize(Decimal("0.01"))
        running_total += amt
        installments.append(PaymentPlanInstallment(due_date=due, amount=amt))

    return PaymentPlan(
        is_applicable=True,
        number_of_installments=num_installments,
        installments=installments,
        total_plan_amount=remaining,
    )


def _suggest_spending_changes(
    request_type: str, text: str, status: AffordabilityStatus
) -> list[SpendingChange]:
    if status not in (
        AffordabilityStatus.AFFORDABLE_WITH_ADJUSTMENTS,
        AffordabilityStatus.NOT_AFFORDABLE,
    ):
        return []

    changes = []
    for category, patterns in DISCRETIONARY_CATEGORY_HINTS.items():
        if _search_any(patterns, text):
            changes.append(
                SpendingChange(
                    category=category,
                    current_monthly_amount=Decimal("200.00"),   # placeholder --
                    suggested_monthly_amount=Decimal("100.00"),  # replace with real
                    rationale=(                                  # transaction data
                        f"Request mentions {category.replace('_', ' ')}; "
                        "reducing this discretionary spend frees up cash flow."
                    ),
                )
            )

    # Type-specific default nudge when no category keywords matched at all,
    # so adjustment-needed responses aren't left with an empty list.
    if not changes and request_type == TYPE_INVESTMENT:
        changes.append(
            SpendingChange(
                category="discretionary_investment",
                current_monthly_amount=Decimal("0.00"),
                suggested_monthly_amount=Decimal("0.00"),
                rationale=(
                    "Investment requests are discretionary by nature; consider "
                    "capping this contribution until essential expenses and "
                    "debt obligations are fully covered."
                ),
            )
        )

    return changes


def _earliest_full_payment_date(status: AffordabilityStatus, plan: PaymentPlan) -> Optional[date]:
    if status == AffordabilityStatus.AFFORDABLE:
        return None
    if plan.is_applicable and plan.installments:
        return plan.installments[-1].due_date
    return date.today() + timedelta(days=90)


def _build_explanation(
    request_type: str,
    status: AffordabilityStatus,
    method: PaymentMethod,
    amount_safe_to_pay: Decimal,
    requested_amount: Decimal,
    plan: PaymentPlan,
) -> str:
    type_label = request_type.replace("_", " ")

    if status == AffordabilityStatus.INSUFFICIENT_DATA:
        return (
            f"The {type_label} request did not include a usable requested amount, "
            "so a definitive affordability decision could not be made."
        )
    if status == AffordabilityStatus.AFFORDABLE:
        return (
            f"For this {type_label} request, {requested_amount} is currently "
            f"affordable in full; recommending {method.value}."
        )
    if plan.is_applicable:
        return (
            f"For this {type_label} request, {amount_safe_to_pay} is safe to pay now. "
            f"The remaining balance is spread across {plan.number_of_installments} "
            f"installments ending {plan.installments[-1].due_date.isoformat()}."
        )
    return (
        f"For this {type_label} request, only {amount_safe_to_pay} of the requested "
        f"{requested_amount} is currently safe to pay; recommending {method.value} "
        "until affordability improves."
    )


def run_agent(request_row: dict) -> FinancialAgentOutput:
    """
    Processes one row from requests.csv and returns a fully populated
    FinancialAgentOutput. Expects request_row to contain (at minimum):
    request_id, type, requested_amount, desired_completion_date, and a
    free-text field (checked under a few common header names).
    """
    request_type = _normalize_type(request_row.get("type", ""))
    requested_amount = _parse_amount(request_row.get("requested_amount", "0"))
    desired_completion_date = _parse_date(request_row.get("desired_completion_date", ""))
    text = (
        request_row.get("request_text")
        or request_row.get("text")
        or request_row.get("description")
        or request_row.get("message")
        or ""
    )

    status, amount_safe_to_pay, needs_installments = _assess_affordability(
        request_type, requested_amount, text
    )
    method = _recommend_payment_method(request_type, status, needs_installments)
    plan = _build_payment_plan(
        requested_amount, amount_safe_to_pay, needs_installments, desired_completion_date
    )
    spending_changes = _suggest_spending_changes(request_type, text, status)
    earliest_full_payment = _earliest_full_payment_date(status, plan)
    explanation = _build_explanation(
        request_type, status, method, amount_safe_to_pay, requested_amount, plan
    )

    return FinancialAgentOutput(
        amount_safe_to_pay=amount_safe_to_pay,
        affordability_status=status,
        recommended_payment_method=method,
        payment_plan=plan,
        earliest_date_for_full_payment=earliest_full_payment,
        spending_changes_needed=spending_changes,
        decision_explanation=explanation,
    )