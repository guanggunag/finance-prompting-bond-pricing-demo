# Finance Prompting Demo: Bond Clean Price vs Dirty Price

This is a small prompt-engineering benchmark for a repeatable finance calculation problem.

The project demonstrates that vague LLM prompts often produce incorrect bond accrued interest and dirty price calculations, while structured prompts make the correct solution much more likely. The prompts can be tested with Claude, DeepSeek, GitHub Copilot Chat, or another LLM. A deterministic Python solver provides the ground truth, and an optional DeepSeek API runner can execute the prompt benchmark automatically.

## Problem

The benchmark asks an LLM to calculate:

- Dollar clean price
- Coupon payment per period
- Accrued fraction
- Accrued interest
- Dirty price

The core identity is:

```text
dirty price = dollar clean price + accrued interest
```

This is a useful prompt-engineering example because the arithmetic is small, but the details are easy for an underspecified LLM prompt to mishandle.

Common mistakes include:

- Treating a clean price quoted per 100 par as the total dollar price.
- Using the annual coupon instead of the coupon per period.
- Ignoring coupon frequency.
- Using Actual/365 when the prompt specifies Actual/Actual or 30/360.
- Adding accrued interest on a coupon date.
- Returning a dirty price without validating the calculation.

## Project Structure

```text
finance-prompting-bond-pricing-demo/
|-- README.md
|-- PROMPT_COMPARISON.md
|-- requirements.txt
|-- data/
|   `-- test_cases.json
|-- prompts/
|   |-- bad_prompts.md
|   `-- good_prompts.md
|-- src/
|   |-- bond_pricing.py
|   |-- run_deepseek_experiment.py
|   `-- run_experiment.py
|-- results/
|   `-- comparison_table.md
`-- tests/
    `-- test_bond_pricing.py
```

## Ground-Truth Solver

The Python solver supports:

- Face value
- Clean price quoted per 100 par
- Annual coupon rate
- Coupon frequency
- Last coupon date
- Settlement date
- Next coupon date
- Day-count convention: `Actual/Actual` and `30/360`

The deterministic calculation sequence is:

```text
dollar clean price = face value * clean price per 100 / 100
coupon per period = face value * annual coupon rate / coupon frequency
accrued fraction = elapsed coupon-period days / full coupon-period days
accrued interest = coupon per period * accrued fraction
dirty price = dollar clean price + accrued interest
```

For `Actual/Actual`, the solver uses actual days elapsed divided by actual days in the coupon period. For `30/360`, it uses the US 30/360 convention.

## Prompt Sets

The project includes two prompt sets:

- `prompts/bad_prompts.md`: 6 vague prompts designed to expose likely LLM failures.
- `prompts/good_prompts.md`: 6 structured prompts that specify formulas, conventions, and validation checks.

To test with an LLM, combine one prompt with one JSON case from `data/test_cases.json`, then compare the answer against the solver output.

See `PROMPT_COMPARISON.md` for the explanation of what the improved prompts teach. The comparison frames the task as skill transfer: the initial prompts are missing the US 30/360 month-end convention, while the improved prompts state that convention explicitly.

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the tests:

```bash
python -m pytest
```

Regenerate the comparison table:

```bash
python src/run_experiment.py
```

The generated summary is written to:

```text
results/comparison_table.md
```

## Optional DeepSeek API Experiment

The DeepSeek runner sends each test case to the model twice:

1. Once with a vague prompt.
2. Once with a structured prompt.

It then parses the model's JSON response and compares the numeric fields against the deterministic Python ground truth.

Do not commit your API key. Set it as an environment variable before running the script.

You can also copy `.env.example` to `.env` and put your real key there. The `.env` file is ignored by git.

PowerShell:

```powershell
$env:DEEPSEEK_API_KEY="your_api_key_here"
$env:DEEPSEEK_MODEL="deepseek-v4-flash"
py src/run_deepseek_experiment.py
```

Bash:

```bash
export DEEPSEEK_API_KEY="your_api_key_here"
export DEEPSEEK_MODEL="deepseek-v4-flash"
python src/run_deepseek_experiment.py
```

To test only the first case while checking that the API setup works:

```bash
python src/run_deepseek_experiment.py --limit 1
```

To run all 6 bad prompts and all 6 good prompts against the hard 30/360 case:

```bash
python src/run_deepseek_experiment.py --case-id case_02_30_360_quarterly_premium --all-prompts --output-stem deepseek_case02_prompt_suite
```

The DeepSeek runner writes:

```text
results/deepseek_outputs.json
results/deepseek_comparison_table.md
```

`results/deepseek_outputs.json` may contain full model responses, so review it before sharing if your prompts or test cases contain private information.

## Test Cases

The benchmark contains 6 parameterized cases:

1. Semiannual coupon bond below par using Actual/Actual.
2. Quarterly coupon bond above par using 30/360.
3. Settlement exactly on a coupon date.
4. Settlement close to the next coupon date.
5. Monthly coupon bond with a non-standard face value.
6. Annual coupon bond above par using 30/360.

These cases make the problem repeatable across different inputs, dates, coupon frequencies, and day-count conventions.

## Key Takeaway

This project highlights a simple point: finance prompts need explicit conventions. A vague prompt may produce an answer that looks reasonable but is wrong. A structured prompt that states the quote convention, coupon frequency, day-count rule, and validation formula is much more likely to match the deterministic ground truth.
