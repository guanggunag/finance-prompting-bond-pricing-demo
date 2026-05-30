# Prompt Comparison: Initial Prompts vs Skill-Teaching Prompts

This file explains the difference between the initial prompts and the improved prompts used in this benchmark.

The goal is not to exploit a model weakness or trick the model into a bad answer. The goal is to show that a finance calculation can be wrong when the prompt does not teach the exact convention, and that the same model can solve it correctly once the missing skill is stated clearly.

## Skill Being Taught

The missing skill is the US 30/360 day-count convention for bond accrued interest.

The hard benchmark case is `case_02_30_360_quarterly_premium`:

```text
face_value = 5000
clean_price_per_100 = 101.25
annual_coupon_rate = 0.045
coupon_frequency = 4
last_coupon_date = 2026-02-28
settlement_date = 2026-04-15
next_coupon_date = 2026-05-31
day_count_convention = 30/360
```

The initial prompts assume a simple or raw 30/360 calculation. That is an incomplete mental model of the convention. It misses the month-end adjustments that matter for February 28 and May 31.

The improved prompts teach the model the missing convention:

```text
If the start date is the last day of February, set D1 = 30.
Else if the start date day is 31, set D1 = 30.
If the adjusted D1 is 30 or 31 and the end date day is 31, set D2 = 30.
days_360 = 360*(Y2 - Y1) + 30*(M2 - M1) + (D2 - D1).
accrued_fraction = days_360(last_coupon_date, settlement_date)
                 / days_360(last_coupon_date, next_coupon_date).
```

## Why The Initial Prompt Fails

For the case above, a raw 30/360 calculation can treat February 28 as day 28 and May 31 as day 31.

That gives:

```text
raw elapsed days = 47
raw full-period days = 93
raw accrued fraction = 47 / 93 = 0.505376
```

Then:

```text
coupon per period = 5000 * 0.045 / 4 = 56.25
raw accrued interest = 56.25 * 0.505376 = 28.427419
raw dirty price = 5062.50 + 28.427419 = 5090.927419
```

This is plausible, but it is not the benchmark ground truth because it does not apply the US 30/360 month-end rules.

## Why The Improved Prompt Works

With the US 30/360 rule:

```text
last coupon date 2026-02-28 is the last day of February, so D1 = 30.
next coupon date 2026-05-31 has D2 = 31, but adjusted D1 is 30, so D2 = 30.
```

For elapsed days from 2026-02-28 to 2026-04-15:

```text
days_360 = 360*(2026 - 2026) + 30*(4 - 2) + (15 - 30)
         = 45
```

For the full coupon period from 2026-02-28 to 2026-05-31:

```text
days_360 = 360*(2026 - 2026) + 30*(5 - 2) + (30 - 30)
         = 90
```

So:

```text
accrued fraction = 45 / 90 = 0.5
coupon per period = 5000 * 0.045 / 4 = 56.25
accrued interest = 56.25 * 0.5 = 28.125
dollar clean price = 5000 * 101.25 / 100 = 5062.50
dirty price = 5062.50 + 28.125 = 5090.625
```

## Prompt Difference Table

| Prompt ID | Initial Prompt Gap | Skill Added By Improved Prompt | Result |
| --- | --- | --- | --- |
| bad_01 vs good_01 | Uses a simple 30/360 idea but does not define the exact convention. | States that clean price is per 100 par and supplies the exact convention instructions. | Good prompt matches ground truth. |
| bad_02 vs good_02 | Keeps printed day numbers without teaching month-end adjustments. | Walks through dollar clean price, coupon per period, accrued fraction, accrued interest, and dirty price. | Good prompt matches ground truth. |
| bad_03 vs good_03 | Provides only the raw days_360 formula, which is incomplete for US 30/360. | Teaches the February month-end and 31st-day adjustments before applying the formula. | Good prompt matches ground truth. |
| bad_04 vs good_04 | Mentions 30/360 but does not validate whether the correct variant was used. | Adds validation that both numerator and denominator use adjusted 30/360 days. | Good prompt matches ground truth. |
| bad_05 vs good_05 | Treats the date calculation as straightforward and misses the convention-specific adjustment. | Calls out the common mistake and instructs the model to use the stated day-count convention. | Good prompt matches ground truth. |
| bad_06 vs good_06 | Uses a quick unadjusted 30/360 approach. | Requires deterministic benchmark output using the corrected formulas and rounded numeric fields. | Good prompt matches ground truth. |

## Summary

The improved prompts work because they teach the model a missing finance convention:

```text
30/360 is not just a raw date subtraction formula.
For this benchmark, it requires US 30/360 month-end adjustments.
```

The comparison demonstrates prompt engineering as skill transfer: once the convention is explicitly taught, the model can apply it repeatedly and match the deterministic Python ground truth.
