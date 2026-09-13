from fastapi import FastAPI

from models import (
    UserProfile,
    PaymentRequest,
    FinancialAgentOutput
)

from agent import financial_agent


app = FastAPI(
    title="Financial Affordability Agent",
    version="1.0"
)


@app.get("/")
def home():
    return {
        "message": "Financial Affordability Agent is running"
    }


@app.post(
    "/analyze",
    response_model=FinancialAgentOutput
)
def analyze(
    user: UserProfile,
    request: PaymentRequest
):
    result = financial_agent(user, request)

    return result