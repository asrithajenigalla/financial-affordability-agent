from decimal import Decimal
# ============================================================
# EXCHANGE RATE DATA
# ============================================================

exchange_rates = [

    # -------------------- 2023 --------------------

    {"date": "2023-10-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2023-10-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2023-10-15", "from": "USD", "to": "IDR", "rate": 15833.33},

    {"date": "2023-11-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2023-11-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2023-11-15", "from": "USD", "to": "IDR", "rate": 15833.33},

    {"date": "2023-12-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2023-12-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2023-12-15", "from": "USD", "to": "IDR", "rate": 15833.33},

    # -------------------- 2024 --------------------

    {"date": "2024-01-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2024-01-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2024-01-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2024-01-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2024-02-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2024-02-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2024-02-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2024-02-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2024-03-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2024-03-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2024-03-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2024-03-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2024-04-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2024-04-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2024-04-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2024-04-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2024-04-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2024-05-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2024-05-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2024-05-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2024-05-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2024-05-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2024-06-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2024-06-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2024-06-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2024-07-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2024-07-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2024-07-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2024-08-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2024-08-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2024-08-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2024-09-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2024-09-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2024-09-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2024-09-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2024-10-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2024-10-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2024-10-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2024-10-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2024-11-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2024-11-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2024-11-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2024-11-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2024-12-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2024-12-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2024-12-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2024-12-15", "from": "USD", "to": "INR", "rate": 83.33},

    # -------------------- 2025 --------------------

    {"date": "2025-01-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2025-01-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2025-01-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2025-01-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2025-02-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2025-02-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2025-02-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2025-02-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2025-03-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2025-03-15", "from": "USD", "to": "IDR", "rate": 15833.33},

    {"date": "2025-04-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2025-04-15", "from": "USD", "to": "IDR", "rate": 15833.33},

    {"date": "2025-05-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2025-05-15", "from": "USD", "to": "IDR", "rate": 15833.33},

    {"date": "2025-06-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2025-06-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2025-06-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2025-06-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2025-07-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2025-07-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2025-07-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2025-07-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2025-08-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2025-08-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2025-08-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2025-08-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2025-08-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2025-09-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2025-09-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2025-09-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2025-09-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2025-09-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2025-10-01", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2025-10-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2025-10-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2025-10-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2025-10-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2025-10-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2025-11-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2025-11-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2025-11-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2025-11-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2025-11-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2025-12-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2025-12-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2025-12-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2025-12-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2025-12-15", "from": "USD", "to": "INR", "rate": 83.33},

    # -------------------- 2026 --------------------

    {"date": "2026-01-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2026-01-15", "from": "EUR", "to": "ZAR", "rate": 20},
    {"date": "2026-01-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2026-01-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2026-01-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2026-02-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2026-02-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2026-02-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2026-02-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2026-03-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2026-03-15", "from": "USD", "to": "EUR", "rate": 0.92},
    {"date": "2026-03-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2026-03-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2026-04-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2026-04-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2026-04-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2026-05-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2026-05-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2026-05-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2026-06-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2026-06-15", "from": "USD", "to": "IDR", "rate": 15833.33},
    {"date": "2026-06-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2026-07-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2026-07-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2026-08-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2026-08-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2026-09-15", "from": "EUR", "to": "USD", "rate": 1.09},
    {"date": "2026-09-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2026-10-15", "from": "USD", "to": "INR", "rate": 83.33},

    {"date": "2026-11-15", "from": "USD", "to": "INR", "rate": 83.33},
]


# ============================================================
# GET DIRECT RATE
# ============================================================
def get_direct_rate(
    from_currency,
    to_currency,
    target_date
):

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return Decimal("1.0")

    matching_rates = []

    for item in exchange_rates:

        if (
            item["from"].upper() == from_currency
            and
            item["to"].upper() == to_currency
            and
            item["date"] <= target_date
        ):

            matching_rates.append(item)

    if not matching_rates:
        return None

    matching_rates.sort(
        key=lambda x: x["date"],
        reverse=True
    )

    return Decimal(
        str(matching_rates[0]["rate"])
    )


# ============================================================
# CONVERT CURRENCY
# ============================================================
def convert_currency(
    amount,
    from_currency,
    to_currency,
    target_date
):

    amount = Decimal(str(amount))

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    # --------------------------------------------------------
    # SAME CURRENCY
    # --------------------------------------------------------

    if from_currency == to_currency:

        return (
            amount,
            Decimal("1.0"),
            "same_currency"
        )

    # --------------------------------------------------------
    # DIRECT
    # --------------------------------------------------------

    direct_rate = get_direct_rate(
        from_currency,
        to_currency,
        target_date
    )

    if direct_rate is not None:

        return (
            amount * direct_rate,
            direct_rate,
            "direct"
        )

    # --------------------------------------------------------
    # REVERSE
    # --------------------------------------------------------

    reverse_rate = get_direct_rate(
        to_currency,
        from_currency,
        target_date
    )

    if reverse_rate is not None:

        if reverse_rate == 0:
            raise ValueError(
                "Exchange rate cannot be zero."
            )

        rate = Decimal("1") / reverse_rate

        return (
            amount * rate,
            rate,
            "reverse"
        )

    # --------------------------------------------------------
    # THROUGH USD
    # --------------------------------------------------------

    from_to_usd = get_direct_rate(
        from_currency,
        "USD",
        target_date
    )

    if from_to_usd is None:

        reverse_from_usd = get_direct_rate(
            "USD",
            from_currency,
            target_date
        )

        if reverse_from_usd is not None:

            if reverse_from_usd == 0:
                raise ValueError(
                    "Exchange rate cannot be zero."
                )

            from_to_usd = (
                Decimal("1") /
                reverse_from_usd
            )

    usd_to_target = get_direct_rate(
        "USD",
        to_currency,
        target_date
    )

    if usd_to_target is None:

        reverse_target_usd = get_direct_rate(
            to_currency,
            "USD",
            target_date
        )

        if reverse_target_usd is not None:

            if reverse_target_usd == 0:
                raise ValueError(
                    "Exchange rate cannot be zero."
                )

            usd_to_target = (
                Decimal("1") /
                reverse_target_usd
            )

    if (
        from_to_usd is not None
        and
        usd_to_target is not None
    ):

        final_rate = (
            from_to_usd *
            usd_to_target
        )

        return (
            amount * final_rate,
            final_rate,
            "via_usd"
        )

    # --------------------------------------------------------
    # NO RATE
    # --------------------------------------------------------

    raise ValueError(
        f"No exchange rate available for "
        f"{from_currency} -> {to_currency} "
        f"on or before {target_date}"
    )