# Good Prompts

These prompts provide explicit finance instructions. Replace the bracketed fields with the values from a test case.

## 1. Structured Dirty Price Prompt

Calculate the dirty price of a bond using the exact inputs below. Treat the clean price as quoted per 100 par, not as a dollar amount.

- Face value: [face_value]
- Clean price quoted per 100 par: [clean_price_per_100]
- Annual coupon rate: [annual_coupon_rate]
- Coupon frequency: [coupon_frequency]
- Last coupon date: [last_coupon_date]
- Settlement date: [settlement_date]
- Next coupon date: [next_coupon_date]
- Day-count convention: [day_count_convention]

Return dollar clean price, coupon per period, accrued fraction, accrued interest, and dirty price.

## 2. Formula-Guided Prompt

Use this calculation sequence:

1. Dollar clean price = face value * clean price quoted per 100 par / 100.
2. Coupon per period = face value * annual coupon rate / coupon frequency.
3. Accrued fraction = elapsed day-count days from last coupon date to settlement date divided by full coupon-period day-count days, using the given day-count convention.
4. Accrued interest = coupon per period * accrued fraction.
5. Dirty price = dollar clean price + accrued interest.

Apply it to the supplied bond inputs and show each intermediate value.

## 3. Day-Count Controlled Prompt

Compute accrued interest and dirty price. If the day-count convention is Actual/Actual, use actual elapsed days divided by actual days in the coupon period.

If the day-count convention is 30/360, do not use actual calendar days. Use the US 30/360 formula for both the elapsed period and the full coupon period:

1. Start with D1 = start date day and D2 = end date day.
2. If the start date is the last day of February, set D1 = 30.
3. Else if the start date day is 31, set D1 = 30.
4. If the adjusted D1 is 30 or 31 and the end date day is 31, set D2 = 30.
5. days_360 = 360*(Y2 - Y1) + 30*(M2 - M1) + (D2 - D1).
6. Accrued fraction = days_360(last coupon date, settlement date) / days_360(last coupon date, next coupon date).

Do not substitute a 365-day approximation or actual calendar days for 30/360.

## 4. Validation Prompt

Solve the bond pricing problem and validate the result before finalizing:

- Confirm that the clean price quote is converted from per 100 par to dollars.
- Confirm that the coupon is divided by the coupon frequency.
- Confirm that settlement on the coupon date gives zero accrued interest.
- Confirm that dirty price equals dollar clean price plus accrued interest.
- If day-count is 30/360, confirm that both numerator and denominator use adjusted 30/360 days, not actual days.

Return a compact JSON object with the numeric results.

## 5. Error-Avoidance Prompt

You are solving a bond accrued interest problem. Common mistakes are using annual coupon instead of coupon per period, treating the clean price quote as dollars, and using actual days when the case says 30/360. Avoid those mistakes and compute the result step by step.

## 6. Repeatable Benchmark Prompt

For each test case, compute the deterministic ground-truth result using only the formulas and conventions below. Do not infer missing conventions or use market shortcuts. Return results rounded to 6 decimal places.

- Dollar clean price = face value * clean price quoted per 100 par / 100.
- Coupon per period = face value * annual coupon rate / coupon frequency.
- For 30/360, use adjusted 30/360 days for both the elapsed period and the full coupon period.
- Accrued interest = coupon per period * accrued fraction.
- Dirty price = dollar clean price + accrued interest.
