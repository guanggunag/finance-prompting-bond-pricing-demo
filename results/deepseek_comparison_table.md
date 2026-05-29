# DeepSeek Comparison Table

| Case | Prompt ID | Prompt Type | Correct? | Reason | Dirty Price Ground Truth | Dirty Price Parsed |
| --- | --- | --- | --- | --- | ---: | ---: |
| case_02_30_360_quarterly_premium | bad_01 | bad | No | coupon_per_period: expected 56.25, got 0.01125; accrued_fraction: expected 0.5, got 0.5053763440860215; accrued_interest: expected 28.125, got 28.42741935483871; dirty_price: expected 5090.625, got 5090.927419354839 | 5090.625000 | 5090.927419354839 |
| case_02_30_360_quarterly_premium | bad_02 | bad | No | accrued_fraction: expected 0.5, got 0.5053763440860215; accrued_interest: expected 28.125, got 28.42741935483871; dirty_price: expected 5090.625, got 5090.927419354839 | 5090.625000 | 5090.927419354839 |
| case_02_30_360_quarterly_premium | bad_03 | bad | No | accrued_fraction: expected 0.5, got 0.1305555556; accrued_interest: expected 28.125, got 7.34375; dirty_price: expected 5090.625, got 5069.84375 | 5090.625000 | 5069.84375 |
| case_02_30_360_quarterly_premium | bad_04 | bad | No | accrued_fraction: expected 0.5, got 0.5108695652173914; accrued_interest: expected 28.125, got 28.73641304347826; dirty_price: expected 5090.625, got 5091.236413043478 | 5090.625000 | 5091.236413043478 |
| case_02_30_360_quarterly_premium | bad_05 | bad | No | accrued_fraction: expected 0.5, got 0.5053763440860215; accrued_interest: expected 28.125, got 28.427419354838708; dirty_price: expected 5090.625, got 5090.927419354839 | 5090.625000 | 5090.927419354839 |
| case_02_30_360_quarterly_premium | bad_06 | bad | No | accrued_fraction: expected 0.5, got 0.5053763440860215; accrued_interest: expected 28.125, got 28.42741935483871; dirty_price: expected 5090.625, got 5090.927419354839 | 5090.625000 | 5090.927419354839 |
| case_02_30_360_quarterly_premium | good_01 | good | Yes | Matches ground truth. | 5090.625000 | 5090.625 |
| case_02_30_360_quarterly_premium | good_02 | good | Yes | Matches ground truth. | 5090.625000 | 5090.625 |
| case_02_30_360_quarterly_premium | good_03 | good | Yes | Matches ground truth. | 5090.625000 | 5090.625 |
| case_02_30_360_quarterly_premium | good_04 | good | Yes | Matches ground truth. | 5090.625000 | 5090.625 |
| case_02_30_360_quarterly_premium | good_05 | good | Yes | Matches ground truth. | 5090.625000 | 5090.625 |
| case_02_30_360_quarterly_premium | good_06 | good | Yes | Matches ground truth. | 5090.625000 | 5090.625 |
