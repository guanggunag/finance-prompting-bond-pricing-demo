# Dataset Plan: Parameterized Bond Pricing Questions for LLM Evaluation

## 1. Purpose

This file describes the planned dataset for the bond pricing LLM benchmark.

The dataset is designed to evaluate whether large language models can consistently interpret, remember, and apply bond pricing conventions across:

1. single-question calculation tasks;
2. multi-document interpretation tasks;
3. multi-turn memory-retention tasks;
4. skill-teaching and transfer tasks;
5. conflicting-rule interpretation tasks.

The dataset will start from a small number of original question templates. Each template will be expanded by changing financial parameters such as coupon rate, clean price, face value, coupon frequency, day-count convention, and settlement date.

The target is to generate more than 100 total questions from a small number of original templates.

## 2. Design Principle

The dataset is not intended to trick the model. The goal is to test whether the model can apply clearly specified financial rules in a consistent and reproducible way.

The benchmark focuses on cases where the correct answer can be computed by a deterministic Python solver. This allows model outputs to be evaluated objectively.

The main failure modes being tested are:

* using the wrong day-count convention;
* treating clean price quoted per 100 par as a total dollar price;
* using annual coupon instead of coupon per period;
* ignoring coupon frequency;
* mixing parameters from different documents;
* forgetting a rule stated earlier in the conversation;
* applying a general rule when a specific bond term should override it.

## 3. Core Financial Fields

Each generated bond pricing question will be based on some or all of the following fields:

```text
case_id
face_value
clean_price_per_100
annual_coupon_rate
coupon_frequency
last_coupon_date
settlement_date
next_coupon_date
day_count_convention
question_type
expected_outputs
```

The expected outputs may include:

```text
dollar_clean_price
coupon_per_period
accrued_fraction
accrued_interest
dirty_price
```

## 4. Parameter Grid

The dataset can be expanded by changing combinations of the following parameters.

### 4.1 Face Value

```text
1000
5000
10000
25000
```

### 4.2 Clean Price Quoted per 100 Par

```text
97.50
98.75
99.50
100.00
101.25
102.50
104.00
```

### 4.3 Annual Coupon Rate

```text
0.035
0.040
0.045
0.050
0.051
0.052
0.053
0.055
0.060
```

### 4.4 Coupon Frequency

```text
1   # annual
2   # semiannual
4   # quarterly
12  # monthly
```

### 4.5 Day-Count Convention

Initial scope:

```text
Actual/Actual
30/360
```

Optional later extension:

```text
Actual/360
Actual/365
30E/360
```

### 4.6 Settlement Date Position

The settlement date can be varied to create different accrued-interest cases:

```text
on_coupon_date
early_in_coupon_period
middle_of_coupon_period
near_next_coupon_date
month_end_case
february_month_end_case
```

## 5. Original Question Templates

The dataset will be generated from a small set of original templates.

## Template 1: Single Bond Dirty Price Calculation

### Goal

Test whether the model can compute accrued interest and dirty price for one bond when all information is provided in a single prompt.

### Input Structure

```text
A bond has the following terms:

Face value: {face_value}
Clean price quoted per 100 par: {clean_price_per_100}
Annual coupon rate: {annual_coupon_rate}
Coupon frequency: {coupon_frequency}
Last coupon date: {last_coupon_date}
Settlement date: {settlement_date}
Next coupon date: {next_coupon_date}
Day-count convention: {day_count_convention}

Calculate:
1. dollar clean price
2. coupon per period
3. accrued fraction
4. accrued interest
5. dirty price
```

### Parameters to Vary

* face value;
* clean price;
* coupon rate;
* coupon frequency;
* date pattern;
* day-count convention.

### Expected Model Skill

The model must correctly apply:

```text
dollar clean price = face value * clean price per 100 / 100
coupon per period = face value * annual coupon rate / coupon frequency
accrued interest = coupon per period * accrued fraction
dirty price = dollar clean price + accrued interest
```

## Template 2: Multi-Document Bond Pricing Task

### Goal

Test whether the model can identify and combine relevant information across multiple short documents.

### Input Structure

```text
Document A: General Bond Pricing Formula
Dirty price equals dollar clean price plus accrued interest.
Dollar clean price equals face value multiplied by clean price quoted per 100 divided by 100.

Document B: Bond Terms
Face value: {face_value}
Clean price quoted per 100 par: {clean_price_per_100}
Annual coupon rate: {annual_coupon_rate}
Coupon frequency: {coupon_frequency}

Document C: Date and Day-Count Information
Last coupon date: {last_coupon_date}
Settlement date: {settlement_date}
Next coupon date: {next_coupon_date}
Day-count convention: {day_count_convention}

Document D: Example Not Used for This Bond
This example may contain a different coupon rate, face value, or day-count convention.

Question:
Using only the relevant information for the target bond, calculate the dirty price.
```

### Parameters to Vary

* position of the relevant document;
* irrelevant example values;
* day-count convention;
* number of documents;
* whether the distracting document contains similar but incorrect parameters.

### Expected Model Skill

The model must avoid mixing parameters across documents.

## Template 3: Memory Retention Task

### Goal

Test whether the model can remember and consistently apply rules stated earlier in a conversation.

### Initial Instruction

```text
For this session, use the following rules unless a later bond-specific instruction explicitly overrides them:

1. Clean prices are quoted per 100 par.
2. Coupon rates are annual rates.
3. Coupon per period equals face value times annual coupon rate divided by coupon frequency.
4. Dirty price equals dollar clean price plus accrued interest.
5. When 30/360 is specified, use the US 30/360 convention.
```

### Follow-Up Questions

The model is then asked a sequence of 10–15 bond pricing questions with different parameters.

Each question may omit some repeated rules, requiring the model to remember the session-level instruction.

### Parameters to Vary

* number of turns before the target question;
* placement of distractor questions;
* whether the day-count convention changes;
* whether the same rule must be applied repeatedly.

### Expected Model Skill

The model must retain the original pricing rules across multiple queries.

## Template 4: Skill Teaching and Transfer Task

### Goal

Test whether the model can learn a missing convention and apply it to new cases.

### Stage 1: Initial Prompt

The model receives an underspecified bond pricing prompt.

Example:

```text
Calculate the dirty price of this bond using the 30/360 day-count convention.
```

This may lead to errors if the model does not apply the correct US 30/360 month-end adjustment.

### Stage 2: Teaching Prompt

The missing convention is then explicitly provided.

Example:

```text
For US 30/360:
1. If the start date is the last day of February, set D1 = 30.
2. Else if the start date day is 31, set D1 = 30.
3. If the adjusted D1 is 30 or 31 and the end date day is 31, set D2 = 30.
4. days_360 = 360*(Y2 - Y1) + 30*(M2 - M1) + (D2 - D1).
```

### Stage 3: Transfer Cases

The model is then tested on new parameterized cases.

### Expected Model Skill

The model should apply the taught convention to new dates and parameters, not just repeat the original example.

## Template 5: Conflicting Information Task

### Goal

Test whether the model can resolve conflicts between general rules and bond-specific instructions.

### Input Structure

```text
Document A: General Rule
Most bonds in this dataset use Actual/Actual unless otherwise stated.

Document B: Target Bond Terms
The target bond uses 30/360.
Face value: {face_value}
Clean price quoted per 100 par: {clean_price_per_100}
Annual coupon rate: {annual_coupon_rate}
Coupon frequency: {coupon_frequency}

Document C: Dates
Last coupon date: {last_coupon_date}
Settlement date: {settlement_date}
Next coupon date: {next_coupon_date}

Question:
Calculate the dirty price of the target bond.
```

### Parameters to Vary

* whether the specific rule appears before or after the general rule;
* whether the general rule and specific rule conflict;
* whether the irrelevant rule appears in an example;
* whether the target bond terms are clearly labeled.

### Expected Model Skill

The model must understand that the bond-specific instruction overrides the general rule.

## 6. Planned Dataset Size

The first version of the dataset can be generated as follows:

| Template Type                    | Approximate Number of Questions |
| -------------------------------- | ------------------------------: |
| Single bond pricing calculation  |                              30 |
| Multi-document bond pricing task |                              25 |
| Memory retention task            |                              20 |
| Skill teaching and transfer task |                              15 |
| Conflicting information task     |                              15 |
| Total                            |                             105 |

This satisfies the requirement that a few original question types can be expanded into more than 100 total questions by changing parameters.

## 7. Ground Truth Generation

Ground truth will be generated using a deterministic Python solver.

For each generated case, the solver will calculate:

```text
dollar_clean_price
coupon_per_period
accrued_fraction
accrued_interest
dirty_price
```

The ground truth will be stored in a structured file such as:

```text
dataset/ground_truth.csv
```

or:

```text
dataset/generated_questions.json
```

Each record should include:

```text
case_id
question_type
input_parameters
prompt_text
ground_truth_outputs
```

## 8. Evaluation Plan

Model outputs will be compared against the deterministic ground truth.

A response will be considered correct if the required numeric fields match the ground truth within a small tolerance.

Possible tolerance:

```text
absolute error <= 1e-6
```

or, for displayed rounded results:

```text
absolute error <= 0.01
```

The evaluation script will classify errors into categories such as:

```text
clean_price_conversion_error
coupon_frequency_error
day_count_error
accrued_fraction_error
accrued_interest_error
dirty_price_identity_error
multi_document_confusion
memory_retention_failure
conflicting_rule_failure
parse_failure
```

## 9. Example Generated Case

```json
{
  "case_id": "single_30_360_001",
  "question_type": "single_bond_pricing",
  "face_value": 5000,
  "clean_price_per_100": 101.25,
  "annual_coupon_rate": 0.045,
  "coupon_frequency": 4,
  "last_coupon_date": "2026-02-28",
  "settlement_date": "2026-04-15",
  "next_coupon_date": "2026-05-31",
  "day_count_convention": "30/360",
  "expected_outputs": {
    "dollar_clean_price": 5062.5,
    "coupon_per_period": 56.25,
    "accrued_fraction": 0.5,
    "accrued_interest": 28.125,
    "dirty_price": 5090.625
  }
}
```

## 10. Dataset Files to Create

Planned files:

```text
dataset/
|-- templates.json
|-- generated_questions.json
|-- ground_truth.csv
|-- README.md
```

Possible supporting scripts:

```text
src/
|-- generate_dataset.py
|-- bond_pricing_solver.py
|-- evaluate_outputs.py
```

## 11. Current Status

The current interview question already provides a starting point for the dataset. It includes several parameterized bond pricing cases and a deterministic solver.

The next step is to expand the dataset from the initial cases into a larger benchmark with more than 100 generated questions across the five template types described above.

## 12. Open Questions for Advisor Feedback

1. Should the first dataset version focus only on clean-to-dirty price conversion, or should it also include yield-based bond pricing?
2. Should the multi-document tasks use short synthetic documents or more realistic mini term sheets?
3. Should memory-retention tasks be evaluated in a single long prompt or as a multi-turn conversation?
4. Which LLMs should be tested first?
5. What level of numerical tolerance should be used for evaluation?
6. Should the first deliverable prioritize dataset generation or solution framework testing?
