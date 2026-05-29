# Comparison Table

This table is generated from the deterministic Python solver. The bad prompt column lists the failure that an underspecified LLM prompt is designed to expose. The good prompt result is checked against the same ground truth for every test case.

| Case | Bad Prompt Expected Failure | Ground Truth Dirty Price | Good Prompt Correct? |
| --- | --- | ---: | --- |
| case_01_actual_actual_semiannual_discount | May treat 98.50 as dollars instead of 98.50 per 100 par. | 999.917127 | Yes |
| case_02_30_360_quarterly_premium | May ignore quarterly frequency and use the annual coupon. | 5090.625000 | Yes |
| case_03_actual_actual_on_coupon_date | May add accrued interest even though settlement is on a coupon date. | 1000.000000 | Yes |
| case_04_30_360_near_next_coupon | May use Actual/365 instead of the specified 30/360 convention. | 10161.666667 | Yes |
| case_05_actual_actual_monthly_small_face | May miss the monthly coupon period and overstate accrued interest. | 2482.678571 | Yes |
| case_06_30_360_annual_premium | May skip quote conversion and validation of clean plus accrued. | 1064.006944 | Yes |

Good prompts are expected to match the solver because they specify quote conversion, coupon frequency, day-count convention, and the dirty price identity.
