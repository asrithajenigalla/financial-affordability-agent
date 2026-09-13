"""
process_requests.py

Reads financial requests from dataset/requests.csv, runs each through
run_agent() (agent_logic.py), validates the output against
FinancialAgentOutput (models.py), and writes a flat CSV to
dataset/output.csv in the exact required column order.

Nested fields (payment_plan, spending_changes_needed) are serialized as
JSON strings within their CSV cell to keep the output flat.

Production safeguards:
- Guarantees strict 1:1 row count with requests.csv: any row that fails
  processing or validation still gets a fallback row (INSUFFICIENT_DATA)
  rather than being dropped.
- Detects duplicate request_ids and disambiguates them in the output
  (original ID preserved with a __dupN suffix) rather than silently
  allowing duplicates through or dropping rows.
- Sanitizes every raw input field (None, non-string types, blank/whitespace
  values) before it reaches run_agent(), so malformed or missing optional
  fields can't propagate untyped values into the parsing logic.
"""

import csv
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from models import AffordabilityStatus, FinancialAgentOutput, PaymentPlan
from agent_logic import run_agent

INPUT_PATH = Path("dataset/requests.csv")
OUTPUT_PATH = Path("dataset/output.csv")

FIELDNAMES = [
    "request_id",
    "amount_safe_to_pay",
    "affordability_status",
    "recommended_payment_method",
    "payment_plan",
    "earliest_date_for_full_payment",
    "spending_changes_needed",
    "decision_explanation",
]

MAX_ERROR_MESSAGE_LENGTH = 300


def sanitize_row(raw_row: dict) -> dict:
    """
    Normalizes every value in a raw CSV row before it reaches run_agent().
    Handles None, non-string types (int/float/NaN-like), and blank/whitespace
    -only values by coercing everything to a clean string (empty string if
    there's genuinely nothing usable). This keeps agent_logic.py's regex and
    Decimal/date parsing from ever receiving None or an unexpected type.
    """
    clean = {}
    for key, value in raw_row.items():
        if value is None:
            clean[key] = ""
        elif isinstance(value, str):
            clean[key] = value.strip()
        else:
            # Covers stray non-string types (e.g. if the row came from a
            # source other than csv.DictReader, or a header had no value).
            clean[key] = str(value).strip()
    return clean


def resolve_request_id(raw_id: str, row_number: int, seen: dict[str, int]) -> str:
    """
    Returns a unique request_id for this row. Empty IDs get a positional
    placeholder; duplicate IDs get a __dupN suffix so uniqueness is
    guaranteed in the output without dropping or merging rows. Logs a
    warning to stderr whenever the ID had to be adjusted.
    """
    base_id = raw_id or f"row_{row_number}"

    if base_id not in seen:
        seen[base_id] = 1
        return base_id

    seen[base_id] += 1
    disambiguated = f"{base_id}__dup{seen[base_id]}"
    print(
        f"[row {row_number}] duplicate request_id '{base_id}' detected -- "
        f"writing output as '{disambiguated}'",
        file=sys.stderr,
    )
    return disambiguated


def serialize_output_row(request_id: str, output: FinancialAgentOutput) -> dict[str, Any]:
    data = output.model_dump(mode="json")

    return {
        "request_id": request_id,
        "amount_safe_to_pay": data["amount_safe_to_pay"],
        "affordability_status": data["affordability_status"],
        "recommended_payment_method": data["recommended_payment_method"],
        "payment_plan": json.dumps(data["payment_plan"], separators=(",", ":")),
        "earliest_date_for_full_payment": data["earliest_date_for_full_payment"] or "",
        "spending_changes_needed": json.dumps(
            data["spending_changes_needed"], separators=(",", ":")
        ),
        "decision_explanation": data["decision_explanation"],
    }


def build_fallback_row(request_id: str, error: Exception, stage: str) -> dict[str, Any]:
    error_message = str(error).replace("\n", " ").replace("\r", " ").strip()
    if len(error_message) > MAX_ERROR_MESSAGE_LENGTH:
        error_message = error_message[:MAX_ERROR_MESSAGE_LENGTH].rstrip() + "...(truncated)"

    fallback_output = FinancialAgentOutput(
        amount_safe_to_pay="0.00",
        affordability_status=AffordabilityStatus.INSUFFICIENT_DATA,
        recommended_payment_method="defer",
        payment_plan=PaymentPlan(is_applicable=False),
        earliest_date_for_full_payment=None,
        spending_changes_needed=[],
        decision_explanation=(
            f"Automated processing failed at {stage} stage for request_id="
            f"{request_id}: {error_message}"
        ),
    )
    return serialize_output_row(request_id, fallback_output)


def main() -> None:
    if not INPUT_PATH.exists():
        print(f"Input file not found: {INPUT_PATH.resolve()}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    processed = 0
    fallback = 0
    duplicates_found = 0
    seen_ids: dict[str, int] = {}

    with INPUT_PATH.open(newline="", encoding="utf-8") as infile, \
         OUTPUT_PATH.open("w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=FIELDNAMES)
        writer.writeheader()

        for i, raw_row in enumerate(reader, start=1):
            row = sanitize_row(raw_row)
            raw_request_id = row.get("request_id", "")

            was_duplicate = raw_request_id in seen_ids
            request_id = resolve_request_id(raw_request_id, i, seen_ids)
            if was_duplicate:
                duplicates_found += 1

            try:
                output = run_agent(row)

                if not isinstance(output, FinancialAgentOutput):
                    output = FinancialAgentOutput.model_validate(output)

                writer.writerow(serialize_output_row(request_id, output))
                processed += 1

            except ValidationError as e:
                print(f"[row {i}] request_id={request_id} validation error: {e}", file=sys.stderr)
                writer.writerow(build_fallback_row(request_id, e, stage="validation"))
                fallback += 1

            except Exception as e:  # noqa: BLE001 - one bad row shouldn't kill the batch
                print(f"[row {i}] request_id={request_id} processing error: {e}", file=sys.stderr)
                writer.writerow(build_fallback_row(request_id, e, stage="processing"))
                fallback += 1

    total = processed + fallback
    print(
        f"Done. {total} rows written ({processed} processed, {fallback} fallback, "
        f"{duplicates_found} duplicate request_id(s) disambiguated). Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()