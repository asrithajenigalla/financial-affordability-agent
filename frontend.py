
import streamlit as st
import requests
import os
import html
from datetime import date
from dotenv import load_dotenv
from google import genai


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    gemini_client = None


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Financial Affordability Agent",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# BACKEND
# =========================================================

BACKEND_URL = "https://financial-affordability-agent.onrender.com/analyze"


# =========================================================
# GEMINI AI REASONING
# =========================================================

def get_ai_reasoning(
    purchase,
    current_balance,
    minimum_balance,
    requested_amount,
    safe_amount,
    affordability_status,
    payment_method,
    financial_priorities,
    protected_expenses
):

    if gemini_client is None:
        return (
            "AI reasoning is currently unavailable.\n\n"
            "Please configure GEMINI_API_KEY in your .env file."
        )

    prompt = f"""
You are a Financial Affordability Assistant.

Analyze the following purchase decision and provide a short,
clear and responsible explanation.

IMPORTANT RULES:
- Do not invent financial data.
- Do not recommend spending more than the maximum safe amount.
- Protect the user's minimum balance.
- Treat education, food and rent as protected expenses when listed.
- Do not make risky investment recommendations.
- Do not encourage unnecessary borrowing.
- Keep the explanation practical and easy for a student to understand.
- Base your reasoning only on the information provided.

Purchase:
{purchase}

Current available balance:
₹{current_balance:.2f}

Minimum balance that must be protected:
₹{minimum_balance:.2f}

Requested purchase amount:
₹{requested_amount:.2f}

Maximum safe amount:
₹{safe_amount:.2f}

Backend affordability status:
{affordability_status}

Backend recommended payment method:
{payment_method}

Financial priorities:
{", ".join(financial_priorities) if financial_priorities else "None specified"}

Protected expenses:
{", ".join(protected_expenses) if protected_expenses else "None specified"}

Give the response using exactly these sections:

1. Decision
2. Why
3. Financial Impact
4. Recommendation

Keep it concise and easy to understand.
"""

    try:

        response = gemini_client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        if response and response.text:
            return response.text

        return "Gemini did not return a financial insight."

    except Exception as e:

        return (
            "AI reasoning could not be generated.\n\n"
            f"Reason: {str(e)}"
        )


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

/* =====================================================
   GENERAL
   ===================================================== */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}


/* =====================================================
   HERO
   ===================================================== */

.hero {
    background: linear-gradient(
        135deg,
        #111827,
        #1f2937
    );

    padding: 35px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 25px;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.2;
    margin: 0;
}

.hero-subtitle {
    font-size: 17px;
    font-weight: 400;
    color: #d1d5db;
    line-height: 1.5;
    margin-top: 10px;
}


/* =====================================================
   SECTION HEADERS
   ===================================================== */

.section-header {
    font-size: 22px;
    font-weight: 750;
    margin-top: 12px;
    margin-bottom: 15px;
}


/* =====================================================
   CARDS
   ===================================================== */

.card {
    background: #ffffff;
    border-radius: 16px;
    padding: 22px;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}

.result-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 30px;
    border: 1px solid #e5e7eb;
    margin-top: 25px;
    text-align: center;
}


/* =====================================================
   SAFE AMOUNT
   ===================================================== */

.safe-label {
    font-size: 15px;
    color: #6b7280;
    margin-bottom: 5px;
}

.safe-amount {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.safe-description {
    font-size: 14px;
    color: #6b7280;
}


/* =====================================================
   STATUS
   ===================================================== */

.status-affordable {
    font-size: 25px;
    font-weight: 800;
    color: #15803d;
}

.status-adjustment {
    font-size: 25px;
    font-weight: 800;
    color: #ca8a04;
}

.status-not {
    font-size: 25px;
    font-weight: 800;
    color: #dc2626;
}


/* =====================================================
   EXPLANATION
   ===================================================== */

.explanation {
    background: #f8fafc;
    border-left: 5px solid #374151;
    padding: 20px;
    border-radius: 10px;
    white-space: pre-wrap;
    line-height: 1.7;
    color: #374151;
}


/* =====================================================
   AI CARD
   ===================================================== */

.ai-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 22px;
    margin-top: 10px;
}


/* =====================================================
   INSTALLMENT CARD
   ===================================================== */

.installment-card {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 10px;
}

.installment-title {
    font-weight: 700;
    font-size: 17px;
}

.installment-details {
    color: #4b5563;
    margin-top: 5px;
}


/* =====================================================
   FOOTER
   ===================================================== */

.footer {
    text-align: center;
    color: #9ca3af;
    padding: 25px;
    font-size: 14px;
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
<div class="hero">
    <div class="hero-title">
        💰 Financial Affordability Agent
    </div>
    <div class="hero-subtitle">
        Smart purchase decisions while protecting your financial safety buffer.
    </div>
</div>
""",
    unsafe_allow_html=True
)


# =========================================================
# NEW ANALYSIS
# =========================================================

reset_col1, reset_col2, reset_col3 = st.columns([5, 1, 5])

with reset_col2:

    if st.button(
        "🔄 New Analysis",
        use_container_width=True,
        key="reset_button"
    ):

        st.session_state.clear()
        st.rerun()


# =========================================================
# INPUT COLUMNS
# =========================================================

col1, col2 = st.columns(2)


# =========================================================
# FINANCIAL INFORMATION
# =========================================================

with col1:

    st.markdown(
        '<div class="section-header">👤 Financial Information</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    current_balance = st.number_input(
        "Current Available Balance (₹)",
        min_value=0.0,
        value=50000.0,
        step=1000.0,
        key="current_balance"
    )

    minimum_balance = st.number_input(
        "Minimum Balance to Keep (₹)",
        min_value=0.0,
        value=10000.0,
        step=1000.0,
        key="minimum_balance"
    )

    requested_amount = st.number_input(
        "Requested Purchase Amount (₹)",
        min_value=0.0,
        value=20000.0,
        step=1000.0,
        key="requested_amount"
    )

    purchase = st.text_input(
        "What do you want to purchase?",
        value="Laptop",
        placeholder="Example: Laptop, Phone, Course...",
        key="purchase"
    )

    completion_date = st.date_input(
        "Desired Completion Date",
        value=date.today(),
        key="completion_date"
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# PAYMENT PREFERENCES
# =========================================================

with col2:

    st.markdown(
        '<div class="section-header">💳 Payment Preferences</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    use_installments = st.checkbox(
        "I am willing to use installments",
        value=True,
        key="use_installments"
    )

    max_months = st.number_input(
        "Maximum Installment Months",
        min_value=1,
        max_value=24,
        value=3,
        step=1,
        disabled=not use_installments,
        key="max_months"
    )

    st.markdown("### 💡 Financial Priorities")

    priority_education = st.checkbox(
        "Education",
        value=True,
        key="priority_education"
    )

    priority_savings = st.checkbox(
        "Savings",
        value=True,
        key="priority_savings"
    )

    st.markdown("### 🛡️ Expenses to Protect")

    protect_education = st.checkbox(
        "Education",
        value=True,
        key="protect_education"
    )

    protect_food = st.checkbox(
        "Food",
        value=True,
        key="protect_food"
    )

    protect_rent = st.checkbox(
        "Rent",
        value=True,
        key="protect_rent"
    )

    st.markdown("### ✂️ Expenses I Can Reduce")

    reduce_entertainment = st.checkbox(
        "Entertainment",
        value=True,
        key="reduce_entertainment"
    )

    st.markdown("### 🛑 Expenses I Can Stop")

    stop_shopping = st.checkbox(
        "Shopping",
        value=True,
        key="stop_shopping"
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# QUICK FINANCIAL CHECK
# =========================================================

safe_amount_preview = max(
    0,
    current_balance - minimum_balance
)

st.markdown("---")

st.markdown(
    '<div class="section-header">📊 Quick Financial Check</div>',
    unsafe_allow_html=True
)

preview1, preview2, preview3 = st.columns(3)

with preview1:

    st.metric(
        "Available Balance",
        f"₹{current_balance:,.2f}"
    )

with preview2:

    st.metric(
        "Protected Minimum",
        f"₹{minimum_balance:,.2f}"
    )

with preview3:

    st.metric(
        "Safe Spending Capacity",
        f"₹{safe_amount_preview:,.2f}"
    )


# =========================================================
# USER PROFILE
# =========================================================

financial_priorities = []

if priority_education:
    financial_priorities.append("education")

if priority_savings:
    financial_priorities.append("savings")


protected_expenses = []

if protect_education:
    protected_expenses.append("education")

if protect_food:
    protected_expenses.append("food")

if protect_rent:
    protected_expenses.append("rent")


expenses_to_reduce = []

if reduce_entertainment:
    expenses_to_reduce.append("entertainment")


expenses_to_stop = []

if stop_shopping:
    expenses_to_stop.append("shopping")


payment_methods = ["full_payment"]

if use_installments:

    payment_methods.extend(
        [
            "partial_payment",
            "installments"
        ]
    )


# =========================================================
# ANALYZE BUTTON
# =========================================================

st.markdown("")

analyze_col1, analyze_col2, analyze_col3 = st.columns(
    [1, 2, 1]
)

with analyze_col2:

    analyze = st.button(
        "🔍 Analyze Affordability",
        use_container_width=True,
        type="primary",
        key="analyze_button"
    )


# =========================================================
# ANALYSIS
# =========================================================

if analyze:

    # =====================================================
    # VALIDATION
    # =====================================================

    if requested_amount <= 0:

        st.error(
            "❌ Please enter a valid purchase amount."
        )

    elif current_balance < minimum_balance:

        st.error(
            "⚠️ Your current balance is already below "
            "the protected minimum."
        )

    elif not purchase.strip():

        st.error(
            "❌ Please enter what you want to purchase."
        )

    else:

        # =================================================
        # PAYLOAD
        # =================================================

        payload = {

            "user": {

                "user_id": "U001",

                "home_currency": "INR",

                "current_available_balance":
                    f"{current_balance:.2f}",

                "minimum_balance_to_keep":
                    f"{minimum_balance:.2f}",

                "financial_priorities":
                    financial_priorities,

                "expense_categories_to_protect":
                    protected_expenses,

                "expense_categories_user_is_willing_to_reduce":
                    expenses_to_reduce,

                "expense_categories_user_is_willing_to_stop":
                    expenses_to_stop,

                "payment_methods_user_will_consider":
                    payment_methods,

                "max_installment_months":
                    int(max_months)
            },

            "request": {

                "request_id": "R003",

                "type": "purchase",

                "requested_amount":
                    f"{requested_amount:.2f}",

                "request_currency": "INR",

                "desired_completion_date":
                    completion_date.isoformat(),

                "request_text":
                    f"I want to purchase {purchase}"
            }
        }


        # =================================================
        # CALL FASTAPI
        # =================================================

        try:

            with st.spinner(
                "🤖 Agent is analyzing your financial situation..."
            ):

                response = requests.post(
                    BACKEND_URL,
                    json=payload,
                    timeout=30
                )


            # =================================================
            # SUCCESS
            # =================================================

            if response.status_code == 200:

                result = response.json()

                st.success(
                    "✅ Analysis completed successfully!"
                )


                # =================================================
                # RESULT VALUES
                # =================================================

                status = result.get(
                    "affordability_status",
                    "unknown"
                )

                safe_amount = result.get(
                    "amount_safe_to_pay",
                    "0.00"
                )

                payment_method = result.get(
                    "recommended_payment_method",
                    "N/A"
                )


                # =================================================
                # SAFE AMOUNT NUMBER
                # =================================================

                try:

                    safe_amount_number = float(
                        safe_amount
                    )

                except (ValueError, TypeError):

                    safe_amount_number = safe_amount_preview


                # =================================================
                # STATUS
                # =================================================

                if status == "affordable":

                    status_text = "✅ AFFORDABLE"
                    status_class = "status-affordable"

                elif status == "affordable_with_adjustments":

                    status_text = (
                        "⚠️ AFFORDABLE WITH ADJUSTMENTS"
                    )

                    status_class = "status-adjustment"

                else:

                    status_text = "❌ NOT AFFORDABLE"
                    status_class = "status-not"


                # =================================================
                # RESULT CARD
                # =================================================

                st.markdown(
                    f"""
<div class="result-card">

    <div class="{status_class}">
        {status_text}
    </div>

    <br>

    <div class="safe-label">
        Maximum Safe Amount
    </div>

    <div class="safe-amount">
        ₹{safe_amount_number:,.2f}
    </div>

    <div class="safe-description">
        Maximum amount you can safely spend
        while protecting your minimum balance.
    </div>

</div>
""",
                    unsafe_allow_html=True
                )


                # =================================================
                # AFFORDABILITY INDICATOR
                # =================================================

                st.markdown(
                    "### 📈 Affordability Indicator"
                )

                if safe_amount_number > 0:

                    percentage = min(
                        (
                            requested_amount
                            / safe_amount_number
                        ) * 100,
                        100
                    )

                else:

                    percentage = 100


                st.progress(
                    int(percentage)
                )


                if requested_amount <= safe_amount_number:

                    st.caption(
                        f"Your purchase uses approximately "
                        f"{percentage:.0f}% of your safe "
                        f"spending capacity."
                    )

                else:

                    excess = (
                        requested_amount
                        - safe_amount_number
                    )

                    st.warning(
                        f"⚠️ The purchase exceeds your current "
                        f"safe spending capacity by "
                        f"₹{excess:,.2f}."
                    )


                # =================================================
                # FINANCIAL SUMMARY
                # =================================================

                st.markdown(
                    "### 📊 Financial Summary"
                )

                c1, c2, c3, c4 = st.columns(4)

                with c1:

                    st.metric(
                        "Available Balance",
                        f"₹{current_balance:,.2f}"
                    )

                with c2:

                    st.metric(
                        "Protected Minimum",
                        f"₹{minimum_balance:,.2f}"
                    )

                with c3:

                    st.metric(
                        "Safe Amount",
                        f"₹{safe_amount_number:,.2f}"
                    )

                with c4:

                    st.metric(
                        "Purchase",
                        f"₹{requested_amount:,.2f}"
                    )


                # =================================================
                # PAYMENT RECOMMENDATION
                # =================================================

                st.markdown(
                    "### 💳 Recommended Payment"
                )

                friendly_payment = (
                    str(payment_method)
                    .replace("_", " ")
                    .title()
                )


                if status == "affordable":

                    st.success(
                        f"💳 Recommended method: "
                        f"**{friendly_payment}**"
                    )

                elif status == "affordable_with_adjustments":

                    st.warning(
                        f"💳 Recommended method: "
                        f"**{friendly_payment}**"
                    )

                else:

                    st.error(
                        f"💳 Recommended method: "
                        f"**{friendly_payment}**"
                    )


                # =================================================
                # PAYMENT PLAN
                # =================================================

                payment_plan = result.get(
                    "payment_plan"
                )

                if (
                    payment_plan
                    and payment_plan.get("is_applicable")
                ):

                    st.markdown(
                        "### 📅 Recommended Payment Plan"
                    )

                    installments = payment_plan.get(
                        "installments",
                        []
                    )

                    for index, installment in enumerate(
                        installments,
                        start=1
                    ):

                        due_date = installment.get(
                            "due_date",
                            "N/A"
                        )

                        amount = installment.get(
                            "amount",
                            "0.00"
                        )

                        st.markdown(
                            f"""
<div class="installment-card">

    <div class="installment-title">
        📅 Installment {index}
    </div>

    <div class="installment-details">
        <b>Amount:</b> ₹{amount}
        &nbsp;&nbsp; | &nbsp;&nbsp;
        <b>Due:</b> {due_date}
    </div>

</div>
""",
                            unsafe_allow_html=True
                        )


                    total = payment_plan.get(
                        "total_plan_amount"
                    )

                    if total:

                        st.info(
                            f"💰 Total planned payment: "
                            f"**₹{total}**"
                        )


                # =================================================
                # EARLIEST FULL PAYMENT
                # =================================================

                earliest_date = result.get(
                    "earliest_date_for_full_payment"
                )

                if earliest_date:

                    st.markdown(
                        "### 📆 Earliest Full Payment Date"
                    )

                    st.info(
                        f"You can make the full payment "
                        f"from **{earliest_date}**."
                    )


                # =================================================
                # SPENDING CHANGES
                # =================================================

                spending_changes = result.get(
                    "spending_changes_needed",
                    []
                )

                if spending_changes:

                    st.markdown(
                        "### ✂️ Suggested Spending Changes"
                    )

                    for change in spending_changes:

                        category = change.get(
                            "category",
                            "Unknown"
                        )

                        action = change.get(
                            "action",
                            "Adjust"
                        )

                        amount = change.get(
                            "amount",
                            "0.00"
                        )

                        reason = change.get(
                            "reason",
                            ""
                        )

                        st.warning(
                            f"**{str(category).title()}**\n\n"
                            f"Action: **{action}**\n\n"
                            f"Amount: ₹{amount}\n\n"
                            f"{reason}"
                        )

                elif status == "affordable":

                    st.success(
                        "🎉 No spending changes are required."
                    )


                # =================================================
                # AGENT DECISION
                # =================================================

                st.markdown(
                    "### 🧠 Agent Decision"
                )

                explanation = result.get(
                    "decision_explanation",
                    "No explanation returned."
                )

                safe_explanation = html.escape(
                    str(explanation)
                )

                st.markdown(
                    f"""
<div class="explanation">
{safe_explanation}
</div>
""",
                    unsafe_allow_html=True
                )


                # =================================================
                # GEMINI AI INSIGHT
                # =================================================

                st.markdown(
                    "### 🤖 AI Financial Insight"
                )

                with st.spinner(
                    "🤖 Gemini is preparing a financial insight..."
                ):

                    ai_reasoning = get_ai_reasoning(
                        purchase=purchase,
                        current_balance=current_balance,
                        minimum_balance=minimum_balance,
                        requested_amount=requested_amount,
                        safe_amount=safe_amount_number,
                        affordability_status=status,
                        payment_method=payment_method,
                        financial_priorities=financial_priorities,
                        protected_expenses=protected_expenses
                    )


                safe_ai_reasoning = html.escape(
                    str(ai_reasoning)
                )

                st.markdown(
                    f"""
<div class="ai-card">
    <div class="explanation">
{safe_ai_reasoning}
    </div>
</div>
""",
                    unsafe_allow_html=True
                )


                # =================================================
                # FINAL DECISION
                # =================================================

                st.markdown(
                    "### 🎯 Final Decision"
                )


                if status == "affordable":

                    st.success(
                        f"✅ You can afford this "
                        f"{purchase.strip()} purchase "
                        f"while keeping "
                        f"₹{minimum_balance:,.2f} "
                        f"as your protected balance."
                    )


                elif status == "affordable_with_adjustments":

                    st.warning(
                        f"⚠️ You may be able to purchase "
                        f"this {purchase.strip()}, but "
                        f"adjustments or installments are "
                        f"recommended to protect your "
                        f"₹{minimum_balance:,.2f} minimum balance."
                    )


                else:

                    st.error(
                        f"❌ This {purchase.strip()} purchase "
                        f"is not currently financially safe "
                        f"while maintaining your "
                        f"₹{minimum_balance:,.2f} "
                        f"protected balance."
                    )


            # =================================================
            # VALIDATION ERROR
            # =================================================

            elif response.status_code == 422:

                st.error(
                    "❌ The backend rejected the request."
                )

                try:

                    st.json(
                        response.json()
                    )

                except Exception:

                    st.code(
                        response.text
                    )


            # =================================================
            # OTHER BACKEND ERROR
            # =================================================

            else:

                st.error(
                    f"❌ Backend returned error "
                    f"{response.status_code}"
                )

                st.code(
                    response.text
                )


        # =====================================================
        # CONNECTION ERROR
        # =====================================================

        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Could not connect to the FastAPI backend."
            )

            st.info(
                "Make sure your backend is running with:\n\n"
                "`python -m uvicorn main:app --reload`"
            )


        # =====================================================
        # TIMEOUT
        # =====================================================

        except requests.exceptions.Timeout:

            st.error(
                "⏳ The backend took too long to respond."
            )


        # =====================================================
        # OTHER ERROR
        # =====================================================

        except Exception as e:

            st.error(
                f"❌ Unexpected error: {str(e)}"
            )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
<div class="footer">
    💰 Financial Affordability Agent
    &nbsp; | &nbsp;
    AI-powered financial decision support
    &nbsp; | &nbsp;
    FastAPI + Streamlit
</div>
""",
    unsafe_allow_html=True
)

