from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# USER PROFILE
# ============================================================

class UserProfile(BaseModel):

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "U001",
                "home_currency": "INR",
                "current_available_balance": "50000.00",
                "minimum_balance_to_keep": "10000.00",
                "financial_priorities": [
                    "education",
                    "savings"
                ],
                "expense_categories_to_protect": [
                    "education",
                    "food",
                    "rent"
                ],
                "expense_categories_user_is_willing_to_reduce": [
                    "entertainment"
                ],
                "expense_categories_user_is_willing_to_stop": [
                    "shopping"
                ],
                "payment_methods_user_will_consider": [
                    "full_payment",
                    "partial_payment",
                    "installments"
                ],
                "max_installment_months": 3
            }
        }
    )

    user_id: str

    home_currency: str

    current_available_balance: Decimal = Field(
        ge=Decimal("0"),
        decimal_places=2
    )

    minimum_balance_to_keep: Decimal = Field(
        ge=Decimal("0"),
        decimal_places=2
    )

    financial_priorities: List[str] = Field(
        default_factory=list
    )

    expense_categories_to_protect: List[str] = Field(
        default_factory=list
    )

    expense_categories_user_is_willing_to_reduce: List[str] = Field(
        default_factory=list
    )

    expense_categories_user_is_willing_to_stop: List[str] = Field(
        default_factory=list
    )

    payment_methods_user_will_consider: List[str] = Field(
        default_factory=list
    )

    max_installment_months: Optional[int] = Field(
        default=None,
        ge=1
    )


# ============================================================
# PAYMENT REQUEST
# ============================================================

class PaymentRequest(BaseModel):

    request_id: str

    type: str

    requested_amount: Decimal = Field(
        gt=Decimal("0"),
        decimal_places=2
    )

    request_currency: str

    desired_completion_date: Optional[date] = None

    request_text: str


# ============================================================
# AFFORDABILITY STATUS
# ============================================================

class AffordabilityStatus(str, Enum):

    AFFORDABLE = "affordable"

    AFFORDABLE_WITH_ADJUSTMENTS = (
        "affordable_with_adjustments"
    )

    NOT_AFFORDABLE = "not_affordable"

    INSUFFICIENT_DATA = "insufficient_data"


# ============================================================
# PAYMENT METHOD
# ============================================================

class PaymentMethod(str, Enum):

    FULL_BALANCE = "full_balance"

    AUTOPAY_MINIMUM = "autopay_minimum"

    MANUAL_INSTALLMENTS = "manual_installments"

    LINE_OF_CREDIT = "line_of_credit"

    DEFER = "defer"


# ============================================================
# PAYMENT PLAN INSTALLMENT
# ============================================================

class PaymentPlanInstallment(BaseModel):

    due_date: date

    amount: Decimal = Field(
        decimal_places=2,
        json_schema_extra={
            "examples": ["20000.00"]
        }
    )


# ============================================================
# PAYMENT PLAN
# ============================================================

class PaymentPlan(BaseModel):

    is_applicable: bool

    number_of_installments: Optional[int] = None

    installments: List[PaymentPlanInstallment] = Field(
        default_factory=list
    )

    total_plan_amount: Optional[Decimal] = Field(
        default=None,
        decimal_places=2,
        json_schema_extra={
            "examples": ["60000.00"]
        }
    )


# ============================================================
# SPENDING CHANGE
# ============================================================

class SpendingChange(BaseModel):

    category: str

    action: str

    amount: Optional[Decimal] = Field(
        default=None,
        decimal_places=2
    )

    reason: Optional[str] = None


# ============================================================
# FINAL AGENT OUTPUT
# ============================================================

class FinancialAgentOutput(BaseModel):

    amount_safe_to_pay: Decimal = Field(
        decimal_places=2,
        json_schema_extra={
            "examples": ["40000.00"]
        }
    )

    affordability_status: AffordabilityStatus

    recommended_payment_method: PaymentMethod

    payment_plan: PaymentPlan

    earliest_date_for_full_payment: Optional[date] = None

    spending_changes_needed: List[SpendingChange] = Field(
        default_factory=list
    )

    decision_explanation: str