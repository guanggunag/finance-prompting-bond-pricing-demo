from __future__ import annotations

import os

from src.run_deepseek_experiment import build_prompt, extract_json_object, load_env_file, score_response


def test_build_good_prompt_includes_structured_instructions() -> None:
    case = {
        "face_value": 1000,
        "clean_price_per_100": 98.5,
        "annual_coupon_rate": 0.06,
        "coupon_frequency": 2,
        "last_coupon_date": "2026-01-15",
        "settlement_date": "2026-04-15",
        "next_coupon_date": "2026-07-15",
        "day_count_convention": "Actual/Actual",
    }
    prompt = build_prompt(case, "Calculate the dirty price.", structured=True)
    assert "clean_price_per_100" in prompt
    assert "US 30/360" in prompt
    assert "do not use actual calendar days" in prompt
    assert "days_360" in prompt
    assert "Round every returned numeric value to 6 decimal places." in prompt


def test_extract_json_object_from_markdown_response() -> None:
    response = '```json\n{"dirty_price": 999.917127}\n```'
    assert extract_json_object(response) == {"dirty_price": 999.917127}


def test_score_response_accepts_matching_numeric_strings() -> None:
    expected = {
        "dollar_clean_price": 985.0,
        "coupon_per_period": 30.0,
        "accrued_fraction": 0.497238,
        "accrued_interest": 14.917127,
        "dirty_price": 999.917127,
    }
    response = """{
      "dollar_clean_price": "985.0",
      "coupon_per_period": 30,
      "accrued_fraction": 0.497238,
      "accrued_interest": 14.917127,
      "dirty_price": 999.917127
    }"""
    assert score_response(response, expected)["correct"] is True


def test_score_response_rejects_wrong_dirty_price() -> None:
    expected = {
        "dollar_clean_price": 985.0,
        "coupon_per_period": 30.0,
        "accrued_fraction": 0.497238,
        "accrued_interest": 14.917127,
        "dirty_price": 999.917127,
    }
    response = """{
      "dollar_clean_price": 985.0,
      "coupon_per_period": 30.0,
      "accrued_fraction": 0.497238,
      "accrued_interest": 14.917127,
      "dirty_price": 985.0
    }"""
    score = score_response(response, expected)
    assert score["correct"] is False
    assert "dirty_price" in score["reason"]


def test_load_env_file_does_not_override_existing_value(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("DEEPSEEK_API_KEY=file_value\nDEEPSEEK_MODEL=deepseek-v4-flash\n", encoding="utf-8")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "existing_value")

    load_env_file(env_file)

    assert "DEEPSEEK_MODEL" in os.environ
    assert os.environ["DEEPSEEK_API_KEY"] == "existing_value"
