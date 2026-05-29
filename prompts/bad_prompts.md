# Bad Prompts

These prompts are intentionally under-specified or naive. They are plausible prompts a user might give to an LLM, but they do not define the exact 30/360 variant or month-end adjustments needed for the benchmark case.

## 1. Basic Dirty Price

Calculate the dirty price using a simple 30/360 accrued-interest calculation without adjusting February month-end or 31st dates.

## 2. Short Answer

Find the final bond price using raw 30/360 day counts. Keep printed day numbers exactly as written, so February 28 stays D=28 and May 31 stays D=31.

## 3. No Day-Count Guidance

Use days_360 = 360*(Y2 - Y1) + 30*(M2 - M1) + (D2 - D1) directly, then calculate dirty price.

## 4. Quote Ambiguity

Use the provided 30/360 convention, but do not worry about special month-end adjustments.

## 5. Coupon Ambiguity

Estimate accrued interest from the straightforward 30/360 day difference. Do not convert February 28 to 30 and do not convert a 31st day to 30.

## 6. Minimal Finance Prompt

Solve quickly using unadjusted 30/360. If the start date is February 28, leave D1=28 in the formula.

## Expected Failure Modes

- Treating a vague 30/360 instruction as the unadjusted formula.
- Missing the US 30/360 month-end adjustment.
- Treating February month-end as day 28 instead of adjusted day 30.
- Treating a 31st end date as 31 when the adjusted start day is 30.
- Returning a plausible dirty price without validating the accrued fraction.
