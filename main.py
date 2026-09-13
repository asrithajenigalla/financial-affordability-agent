from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
import traceback

from models import (
    UserProfile,
    PaymentRequest,
    FinancialAgentOutput
)

from agent import financial_agent


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Financial Affordability Agent",
    version="1.0",
    description=(
        "A deterministic financial affordability engine "
        "with Gemini-powered explanations."
    )
)


# ============================================================
# REQUEST MODEL
# ============================================================

class AnalyzeRequest(BaseModel):

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user": {
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
                },
                "request": {
                    "request_id": "R003",
                    "type": "purchase",
                    "requested_amount": "20000.00",
                    "request_currency": "INR",
                    "desired_completion_date": "2026-09-15",
                    "request_text": "I want to purchase a laptop"
                }
            }
        }
    )

    user: UserProfile
    request: PaymentRequest


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Financial Affordability Agent is running",
        "version": "1.0"
    }


# ============================================================
# ANALYZE
# ============================================================

@app.post(
    "/analyze",
    response_model=FinancialAgentOutput
)
def analyze(data: AnalyzeRequest):

    print("\n" + "=" * 70)
    print("ANALYZE REQUEST RECEIVED")
    print("=" * 70)

    try:

        print("User object:", data.user)
        print("Request object:", data.request)

        print("\nCalling financial_agent()...")

        result = financial_agent(
            data.user,
            data.request
        )

        print("\nfinancial_agent() completed successfully.")
        print("Result:", result)

        print("=" * 70 + "\n")

        return result

    except ValueError as exc:

        print("\nVALUE ERROR:")
        traceback.print_exc()

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        print("\n" + "=" * 70)
        print("FINANCIAL AGENT ERROR")
        print("=" * 70)

        traceback.print_exc()

        print("=" * 70 + "\n")

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )