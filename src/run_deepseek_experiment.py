from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

try:
    from bond_pricing import bond_input_from_dict, price_bond
except ModuleNotFoundError:
    from src.bond_pricing import bond_input_from_dict, price_bond


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "test_cases.json"
OUTPUT_PATH = ROOT / "results" / "deepseek_outputs.json"
SUMMARY_PATH = ROOT / "results" / "deepseek_comparison_table.md"

DEEPSEEK_CHAT_COMPLETIONS_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-v4-flash"
ENV_PATH = ROOT / ".env"
NUMERIC_FIELDS = [
    "dollar_clean_price",
    "coupon_per_period",
    "accrued_fraction",
    "accrued_interest",
    "dirty_price",
]


BAD_PROMPTS = [
    "Calculate the dirty price using a simple 30/360 accrued-interest calculation without adjusting February month-end or 31st dates.",
    "Find the final bond price using raw 30/360 day counts. Keep printed day numbers exactly as written, so February 28 stays D=28 and May 31 stays D=31.",
    "Use days_360 = 360*(Y2 - Y1) + 30*(M2 - M1) + (D2 - D1) directly, then calculate dirty price.",
    "Use the provided 30/360 convention, but do not worry about special month-end adjustments.",
    "Estimate accrued interest from the straightforward 30/360 day difference. Do not convert February 28 to 30 and do not convert a 31st day to 30.",
    "Solve quickly using unadjusted 30/360. If the start date is February 28, leave D1=28 in the formula.",
]


GOOD_PROMPTS = [
    "Calculate the dirty price using the exact formulas and conventions supplied.",
    "Use a step-by-step bond accrued interest calculation and return all intermediate values.",
    "Follow the specified day-count convention exactly. Do not use a 365-day approximation.",
    "Validate that dirty price equals dollar clean price plus accrued interest.",
    "Avoid common mistakes: clean price is per 100 par, coupon must be per period, and day count must match the input.",
    "Return deterministic benchmark output rounded to 6 decimal places.",
]


SYSTEM_PROMPT = """You are a fixed-income calculation assistant.
Return only a JSON object with these numeric fields:
dollar_clean_price, coupon_per_period, accrued_fraction, accrued_interest, dirty_price.
Do not include markdown or explanatory text."""


GOOD_INSTRUCTIONS = """Use this exact calculation sequence:
1. dollar_clean_price = face_value * clean_price_per_100 / 100
2. coupon_per_period = face_value * annual_coupon_rate / coupon_frequency
3. accrued_fraction = elapsed day-count days from last_coupon_date to settlement_date divided by full coupon-period day-count days from last_coupon_date to next_coupon_date
4. For Actual/Actual, use actual elapsed days and actual full coupon-period days.
5. If the day-count convention is 30/360, do not use actual calendar days. Use the US 30/360 formula below for both the numerator and denominator:
   a. Start with D1 = start date day and D2 = end date day.
   b. If the start date is the last day of February, set D1 = 30.
   c. Else if the start date day is 31, set D1 = 30.
   d. If the adjusted D1 is 30 or 31 and the end date day is 31, set D2 = 30.
   e. days_360 = 360*(Y2 - Y1) + 30*(M2 - M1) + (D2 - D1).
   f. accrued_fraction = days_360(last_coupon_date, settlement_date) / days_360(last_coupon_date, next_coupon_date).
6. accrued_interest = coupon_per_period * accrued_fraction
7. dirty_price = dollar_clean_price + accrued_interest
Round every returned numeric value to 6 decimal places."""


def load_cases() -> list[dict[str, Any]]:
    with DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_env_file(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def case_input_payload(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "face_value": case["face_value"],
        "clean_price_per_100": case["clean_price_per_100"],
        "annual_coupon_rate": case["annual_coupon_rate"],
        "coupon_frequency": case["coupon_frequency"],
        "last_coupon_date": case["last_coupon_date"],
        "settlement_date": case["settlement_date"],
        "next_coupon_date": case["next_coupon_date"],
        "day_count_convention": case["day_count_convention"],
    }


def build_prompt(case: dict[str, Any], prompt_text: str, structured: bool) -> str:
    lines = [
        prompt_text,
        "",
        "Bond inputs:",
        json.dumps(case_input_payload(case), indent=2),
    ]
    if structured:
        lines.extend(["", GOOD_INSTRUCTIONS])
    return "\n".join(lines)


def call_deepseek(api_key: str, model: str, user_prompt: str, timeout: int = 60) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        DEEPSEEK_CHAT_COMPLETIONS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek API error {exc.code}: {detail}") from exc

    return body["choices"][0]["message"]["content"]


def extract_json_object(text: str) -> dict[str, Any] | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def score_response(text: str, expected: dict[str, float], tolerance: float = 1e-4) -> dict[str, Any]:
    parsed = extract_json_object(text)
    if parsed is None:
        return {"correct": False, "reason": "No parseable JSON object.", "parsed": None}

    errors: dict[str, str] = {}
    for field in NUMERIC_FIELDS:
        if field not in parsed:
            errors[field] = "missing"
            continue
        try:
            observed = float(parsed[field])
        except (TypeError, ValueError):
            errors[field] = f"not numeric: {parsed[field]!r}"
            continue
        if abs(observed - expected[field]) > tolerance:
            errors[field] = f"expected {expected[field]}, got {observed}"

    return {
        "correct": not errors,
        "reason": "Matches ground truth." if not errors else "; ".join(
            f"{field}: {reason}" for field, reason in errors.items()
        ),
        "parsed": parsed,
    }


def select_cases(cases: list[dict[str, Any]], case_id: str | None, limit: int | None) -> list[dict[str, Any]]:
    if case_id is not None:
        cases = [case for case in cases if case["id"] == case_id]
        if not cases:
            raise ValueError(f"Unknown case id: {case_id}")
    if limit is not None:
        cases = cases[:limit]
    return cases


def prompt_pairs_for_case(case_index: int, all_prompts: bool) -> list[tuple[str, str, str, bool]]:
    if all_prompts:
        bad_pairs = [
            (f"bad_{index:02d}", "bad", prompt, False)
            for index, prompt in enumerate(BAD_PROMPTS, start=1)
        ]
        good_pairs = [
            (f"good_{index:02d}", "good", prompt, True)
            for index, prompt in enumerate(GOOD_PROMPTS, start=1)
        ]
        return bad_pairs + good_pairs

    return [
        (f"bad_{case_index + 1:02d}", "bad", BAD_PROMPTS[case_index % len(BAD_PROMPTS)], False),
        (f"good_{case_index + 1:02d}", "good", GOOD_PROMPTS[case_index % len(GOOD_PROMPTS)], True),
    ]


def run_experiment(
    api_key: str,
    model: str,
    limit: int | None = None,
    sleep_seconds: float = 0.2,
    case_id: str | None = None,
    all_prompts: bool = False,
) -> list[dict[str, Any]]:
    cases = load_cases()
    cases = select_cases(cases, case_id=case_id, limit=limit)

    records: list[dict[str, Any]] = []
    for index, case in enumerate(cases):
        expected = price_bond(bond_input_from_dict(case)).rounded()
        for prompt_id, prompt_type, prompt_text, structured in prompt_pairs_for_case(index, all_prompts):
            user_prompt = build_prompt(case, prompt_text, structured=structured)
            content = call_deepseek(api_key, model, user_prompt)
            score = score_response(content, expected)
            records.append(
                {
                    "case_id": case["id"],
                    "prompt_id": prompt_id,
                    "prompt_type": prompt_type,
                    "model": model,
                    "prompt": user_prompt,
                    "raw_response": content,
                    "ground_truth": expected,
                    "score": score,
                }
            )
            time.sleep(sleep_seconds)
    return records


def result_paths(output_stem: str) -> tuple[Path, Path]:
    return (
        ROOT / "results" / f"{output_stem}_outputs.json",
        ROOT / "results" / f"{output_stem}_comparison_table.md",
    )


def write_outputs(records: list[dict[str, Any]], output_stem: str) -> tuple[Path, Path]:
    output_path, summary_path = result_paths(output_stem)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    rows = [
        "# DeepSeek Comparison Table",
        "",
        "| Case | Prompt ID | Prompt Type | Correct? | Reason | Dirty Price Ground Truth | Dirty Price Parsed |",
        "| --- | --- | --- | --- | --- | ---: | ---: |",
    ]
    for record in records:
        parsed = record["score"]["parsed"] or {}
        parsed_dirty_price = parsed.get("dirty_price", "")
        rows.append(
            "| {case_id} | {prompt_id} | {prompt_type} | {correct} | {reason} | {truth:.6f} | {parsed_dirty_price} |".format(
                case_id=record["case_id"],
                prompt_id=record["prompt_id"],
                prompt_type=record["prompt_type"],
                correct="Yes" if record["score"]["correct"] else "No",
                reason=str(record["score"]["reason"]).replace("|", "\\|"),
                truth=record["ground_truth"]["dirty_price"],
                parsed_dirty_price=parsed_dirty_price,
            )
        )
    summary_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return output_path, summary_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the bond-pricing prompt benchmark against DeepSeek.")
    parser.add_argument("--model", default=os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL))
    parser.add_argument("--limit", type=int, default=None, help="Optional number of test cases to run.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Seconds to sleep between API calls.")
    parser.add_argument("--case-id", default=None, help="Optional case id to run.")
    parser.add_argument("--all-prompts", action="store_true", help="Run every bad and good prompt for each selected case.")
    parser.add_argument("--output-stem", default="deepseek", help="Output file stem under results/.")
    return parser.parse_args()


def main() -> None:
    load_env_file()
    args = parse_args()
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit(
            "Missing DEEPSEEK_API_KEY. Set it as an environment variable before running this script."
        )

    records = run_experiment(
        api_key=api_key,
        model=args.model,
        limit=args.limit,
        sleep_seconds=args.sleep,
        case_id=args.case_id,
        all_prompts=args.all_prompts,
    )
    output_path, summary_path = write_outputs(records, output_stem=args.output_stem)
    print(f"Wrote {output_path}")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
