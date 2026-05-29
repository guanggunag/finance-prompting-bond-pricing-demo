from __future__ import annotations

import json
from pathlib import Path

try:
    from bond_pricing import bond_input_from_dict, price_bond
except ModuleNotFoundError:
    from src.bond_pricing import bond_input_from_dict, price_bond


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "test_cases.json"
RESULTS_PATH = ROOT / "results" / "comparison_table.md"


BAD_PROMPT_FAILURES = {
    "case_01_actual_actual_semiannual_discount": "May treat 98.50 as dollars instead of 98.50 per 100 par.",
    "case_02_30_360_quarterly_premium": "May ignore quarterly frequency and use the annual coupon.",
    "case_03_actual_actual_on_coupon_date": "May add accrued interest even though settlement is on a coupon date.",
    "case_04_30_360_near_next_coupon": "May use Actual/365 instead of the specified 30/360 convention.",
    "case_05_actual_actual_monthly_small_face": "May miss the monthly coupon period and overstate accrued interest.",
    "case_06_30_360_annual_premium": "May skip quote conversion and validation of clean plus accrued.",
}


def load_cases() -> list[dict]:
    with DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_table() -> str:
    rows = [
        "# Comparison Table",
        "",
        "This table is generated from the deterministic Python solver. The bad prompt column lists the failure that an underspecified LLM prompt is designed to expose. The good prompt result is checked against the same ground truth for every test case.",
        "",
        "| Case | Bad Prompt Expected Failure | Ground Truth Dirty Price | Good Prompt Correct? |",
        "| --- | --- | ---: | --- |",
    ]

    for case in load_cases():
        result = price_bond(bond_input_from_dict(case)).rounded()
        expected = case["expected"]
        correct = result == expected
        rows.append(
            "| {case_id} | {failure} | {dirty_price:.6f} | {correct} |".format(
                case_id=case["id"],
                failure=BAD_PROMPT_FAILURES[case["id"]],
                dirty_price=result["dirty_price"],
                correct="Yes" if correct else "No",
            )
        )

    rows.append("")
    rows.append("Good prompts are expected to match the solver because they specify quote conversion, coupon frequency, day-count convention, and the dirty price identity.")
    return "\n".join(rows) + "\n"


def main() -> None:
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(build_table(), encoding="utf-8")
    print(f"Wrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()
