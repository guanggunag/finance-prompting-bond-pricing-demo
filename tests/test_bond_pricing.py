from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.bond_pricing import (
    accrued_fraction,
    bond_input_from_dict,
    parse_date,
    price_bond,
    thirty_360_us_days,
)


ROOT = Path(__file__).resolve().parents[1]


def load_cases() -> list[dict]:
    with (ROOT / "data" / "test_cases.json").open(encoding="utf-8") as handle:
        return json.load(handle)


@pytest.mark.parametrize("case", load_cases(), ids=lambda case: case["id"])
def test_price_bond_matches_expected_ground_truth(case: dict) -> None:
    result = price_bond(bond_input_from_dict(case)).rounded()
    assert result == case["expected"]


def test_actual_actual_fraction_uses_coupon_period_days() -> None:
    fraction = accrued_fraction(
        parse_date("2026-01-15"),
        parse_date("2026-04-15"),
        parse_date("2026-07-15"),
        "Actual/Actual",
    )
    assert round(fraction, 6) == 0.497238


def test_thirty_360_us_handles_month_end_dates() -> None:
    assert thirty_360_us_days(parse_date("2026-02-28"), parse_date("2026-05-31")) == 90


def test_settlement_outside_coupon_period_is_rejected() -> None:
    with pytest.raises(ValueError, match="within the coupon period"):
        accrued_fraction(
            parse_date("2026-01-15"),
            parse_date("2026-08-01"),
            parse_date("2026-07-15"),
            "Actual/Actual",
        )
