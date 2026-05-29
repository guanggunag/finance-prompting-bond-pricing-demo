# Finance Prompting Demo for Bond Clean Price vs Dirty Price

This is a small prompt-engineering benchmark that demonstrates how structured prompts can improve an LLM's accuracy on a repeatable finance calculation problem.

The project focuses on a common fixed-income task: calculating **accrued interest** and **dirty price** from a quoted **clean price**. This problem is intentionally small, but it contains several details that LLMs often mishandle when the prompt is underspecified.

## Objective

The goal is to show that an LLM may produce incorrect answers when given vague finance prompts, but can produce correct and repeatable outputs when the prompt includes clear financial conventions, formulas, and validation checks.

In this project, I compare:

1. **Vague prompts** that often lead to incorrect or incomplete bond pricing calculations.
2. **Structured prompts** that explicitly guide the model through the correct fixed-income logic.

A deterministic Python solver is used as the ground truth.

## Finance Problem

The benchmark asks the model to calculate:

* Accrued interest
* Dirty price
* Dollar clean price
* Coupon payment per period
* Accrued fraction based on the day-count convention

The basic relationship is:

```text
Dirty Price = Dollar Clean Price + Accrued Interest
```

However, the calculation can easily go wrong if the model does not properly handle:

* Clean price quoted per 100 par
* Face value conversion
* Coupon frequency
* Coupon payment per period
* Settlement date
* Last and next coupon dates
* Day-count convention
* Accrued interest fraction

## Why This Problem Is Useful

This problem is small enough to be easy to inspect, but detailed enough to expose common LLM mistakes.

Without structured instructions, an LLM may:

* Treat the clean price as a dollar amount instead of a quote per 100 par
* Use the annual coupon instead of the coupon per period
* Ignore the coupon frequency
* Use the wrong day-count convention
* Miscalculate accrued interest
* Return a dirty price without checking the arithmetic

With structured prompts, the model is instructed to follow the correct calculation sequence and validate the result.

## Methodology

For each test case, the project compares the model's output under two settings:

### 1. Vague Prompt

The model receives a short, underspecified prompt such as:

```text
Calculate the dirty price of this bond.
```

These prompts intentionally leave out detailed instructions about quote convention, coupon frequency, day count, and validation.

### 2. Structured Prompt

The model receives a more explicit prompt that tells it to:

* Treat clean price as quoted per 100 par
* Convert clean price into dollar clean price
* Compute coupon payment per period
* Use the specified day-count convention
* Calculate accrued interest
* Add accrued interest to dollar clean price
* Return the result in a structured format
* Check that the arithmetic is internally consistent

## Example Calculation Logic

For a bond with:

* Face value: 1,000
* Clean price: 98.50
* Annual coupon rate: 6%
* Coupon frequency: 2
* Last coupon date: 2026-01-15
* Settlement date: 2026-04-15
* Next coupon date: 2026-07-15

The correct logic is:

```text
Dollar clean price = 1,000 × 98.50 / 100
Coupon per period = 1,000 × 6% / 2
Accrued fraction = days from last coupon date to settlement date / days in coupon period
Accrued interest = coupon per period × accrued fraction
Dirty price = dollar clean price + accrued interest
```

## Project Structure

```text
finance-prompting-bond-pricing-demo/
├── README.md
├── requirements.txt
├── data/
│   └── test_cases.json
├── prompts/
│   ├── bad_prompts.md
│   └── good_prompts.md
├── src/
│   ├── bond_pricing.py
│   └── run_experiment.py
├── results/
│   └── comparison_table.md
└── tests/
    └── test_bond_pricing.py
```

## Planned Test Cases

The benchmark uses multiple parameterized cases so that the problem is repeatable across different inputs.

Examples include:

1. Semiannual coupon bond with Actual/Actual day count
2. Quarterly coupon bond
3. Bond settling exactly on a coupon date
4. Bond settling close to the next coupon date
5. Clean price quoted below par
6. Clean price quoted above par

Each case can be tested using both vague and structured prompts.

## Expected Result

The expected result is a comparison table showing that vague prompts are more likely to produce errors, while structured prompts produce outputs that match the Python ground truth.

Example format:

| Case   | Vague Prompt Error                          | Structured Prompt Result | Correct? |
| ------ | ------------------------------------------- | ------------------------ | -------- |
| Case 1 | Forgot clean price conversion               | Matches ground truth     | Yes      |
| Case 2 | Used annual coupon instead of period coupon | Matches ground truth     | Yes      |
| Case 3 | Incorrect day-count treatment               | Matches ground truth     | Yes      |
| Case 4 | Did not validate dirty price formula        | Matches ground truth     | Yes      |

## Key Takeaway

This project highlights a simple but important point: in finance workflows, prompt quality can materially affect model correctness.

Even for a basic bond pricing problem, an LLM may make subtle financial calculation mistakes when the prompt is vague. Clear prompt instructions, explicit formulas, and validation checks can make the output more reliable and repeatable.
