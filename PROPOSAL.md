# Project Proposal: Evaluating LLM Multi-Document Reasoning and Memory Retention in Bond Pricing Tasks

## 1. Project Motivation

Large language models are increasingly used to assist with financial reasoning, document interpretation, and quantitative workflows. However, even when a model can solve a single well-specified calculation, it may still make mistakes when the task involves multiple documents, repeated queries, or rules that must be remembered over time.

Bond pricing is a suitable controlled domain for studying these issues because it has deterministic ground truth and clear convention-sensitive calculations. A small change in the interpretation of a pricing convention, such as the day-count rule or coupon frequency, can lead to an incorrect result even if the final answer appears reasonable.

The goal of this project is not simply to test whether an LLM can calculate a bond price. Instead, the project uses bond pricing as a controlled financial benchmark to evaluate whether an LLM can consistently retrieve, remember, and apply pricing rules across multi-document and multi-turn settings.

## 2. Research Questions

This project will focus on two LLM reliability problems:

### 2.1 Multi-Document Interpretation

When multiple documents are provided to an LLM, the model may confuse information across documents, ignore relevant constraints, or apply rules from the wrong source.

In the bond pricing setting, this may appear as:

* using the wrong day-count convention;
* mixing parameters from different bond cases;
* applying a general rule when a more specific bond term should override it;
* confusing examples with the actual target problem;
* failing to identify which document contains the relevant pricing rule.

The project will test whether LLMs can correctly identify and apply the relevant bond pricing information when the inputs are split across multiple short documents.

### 2.2 Memory Retention Over Time

LLMs may also lose track of facts or rules over a long conversation. A rule stated earlier in the interaction may be forgotten or inconsistently applied after several follow-up questions.

In the bond pricing setting, this may appear as:

* forgetting that clean prices are quoted per 100 par;
* forgetting to divide the annual coupon by the coupon frequency;
* forgetting the correct day-count convention after several queries;
* switching between Actual/Actual and 30/360 without justification;
* failing to apply a previously taught convention to later parameterized cases.

The project will test whether LLMs can maintain consistent bond pricing rules over a sequence of related questions.

## 3. Scope of the Project

This project will focus on a limited but testable set of bond pricing tasks. The initial scope will include:

* clean price to dirty price conversion;
* accrued interest calculation;
* coupon per period calculation;
* Actual/Actual and 30/360 day-count conventions;
* settlement date, last coupon date, and next coupon date handling;
* parameterized test cases with deterministic ground truth.

If time allows, the project may extend to additional bond pricing features, such as yield-based pricing, additional day-count conventions, or more realistic mini term-sheet inputs. These extensions will be treated as optional rather than guaranteed deliverables.

## 4. Literature Survey Plan

A focused literature survey will be conducted before and during the early stage of the project. The purpose of the literature survey is to understand existing research on LLM reliability problems that are relevant to this project, and to use that understanding to design a small but well-scoped benchmark.

At this proposal stage, I will not list unverified paper titles or citations. The exact paper list will be added after the sources have been reviewed.

The literature survey will focus on the following areas:

### 4.1 LLM Multi-Document Reasoning

This part will review work on how LLMs process multiple documents or multiple pieces of context. The goal is to understand common failure modes such as cross-document confusion, missed constraints, and incorrect synthesis across sources.

This is directly related to the bond pricing benchmark because bond terms, pricing conventions, and examples can be separated into different documents.

### 4.2 Long-Context Reasoning and Context Degradation

This part will review work on how LLM performance changes as the context becomes longer. The goal is to understand whether models tend to over-weight recent information, ignore earlier information, or lose important details in the middle of the context.

This is relevant because a bond pricing task may require the model to remember pricing rules introduced earlier in a long prompt or conversation.

### 4.3 Memory Retention Across Multi-Turn Interactions

This part will review work on LLM memory and consistency over multi-turn conversations. The goal is to understand how models retain, summarize, or forget user-provided facts across multiple queries.

This is relevant because the project will include multi-turn bond pricing tasks where the model must continue applying previously stated rules.

### 4.4 Retrieval-Augmented Generation and External Memory

This part will review approaches that use retrieval, external memory, structured rule stores, or summaries to improve factual consistency and reduce forgetting.

This will help inform the solution framework for the project, especially if the benchmark shows that a model forgets previously stated pricing rules.

### 4.5 LLM Numerical Reasoning and Financial Reasoning

This part will review work on LLM performance in numerical reasoning and finance-related reasoning tasks. The goal is to understand how LLMs make mistakes in calculation-heavy domains and how structured prompting or verification can reduce those mistakes.

This is relevant because bond pricing requires both financial convention interpretation and numerical calculation.

## 5. Dataset Design

The project will create a small parameterized bond pricing dataset. The dataset will start with a few original question templates. Each template can be expanded into many questions by changing parameters such as coupon rate, clean price, face value, coupon frequency, day-count convention, and settlement date.

The goal is to generate more than 100 test questions from a small number of original templates.

### 5.1 Template Type 1: Single Bond Pricing Calculation

A basic template will ask the model to compute accrued interest and dirty price for one bond.

Example parameters:

* face value;
* clean price quoted per 100 par;
* annual coupon rate;
* coupon frequency;
* last coupon date;
* settlement date;
* next coupon date;
* day-count convention.

Expected outputs:

* dollar clean price;
* coupon per period;
* accrued fraction;
* accrued interest;
* dirty price.

### 5.2 Template Type 2: Multi-Document Bond Pricing Task

This template will split the relevant information across several short documents.

Example structure:

* Document A: general pricing formula;
* Document B: bond-specific terms;
* Document C: day-count convention definition;
* Document D: irrelevant example or potentially confusing information.

The model will be asked to calculate the dirty price using only the relevant information.

This tests whether the model can identify the correct source and avoid mixing information across documents.

### 5.3 Template Type 3: Memory Retention Task

This template will provide a rule at the beginning of a conversation, then ask a sequence of related questions.

Example initial instruction:

“All clean prices in this session are quoted per 100 par. When 30/360 is specified, use the US 30/360 convention. Always compute coupon per period before calculating accrued interest.”

The model will then answer 10–15 related bond pricing questions. The experiment will test whether the model continues to apply the original rule correctly.

### 5.4 Template Type 4: Skill Teaching and Transfer Task

This template will first test whether the model makes an error under an underspecified prompt. Then the missing convention will be explicitly taught. The model will then be tested on new parameterized cases.

This evaluates whether the model can apply a newly taught pricing convention to similar but not identical cases.

### 5.5 Template Type 5: Conflicting Information Task

This template will include both general rules and bond-specific exceptions.

For example, one document may provide a general Actual/Actual rule, while the specific bond terms state that the target bond uses 30/360. The model must identify which rule applies.

This tests whether the model can correctly handle rule priority and avoid using irrelevant context.

See DATASET_PLAN.md for the detailed parameterized dataset design.

## 6. Ground Truth and Evaluation

A deterministic Python solver will be used to generate ground-truth answers for each test case. The solver will compute the required outputs using explicit formulas and day-count conventions.

The model output will be compared against ground truth using numeric tolerances.

Evaluation metrics may include:

* exact or tolerance-based correctness;
* error type classification;
* frequency of day-count convention errors;
* frequency of clean-price conversion errors;
* frequency of coupon-frequency errors;
* performance decay across multi-turn queries;
* performance difference between baseline prompting and improved framework prompting.

The project will also include qualitative error analysis to identify common failure modes.

## 7. Initial Solution Framework

The proposed solution framework will be intentionally simple and testable. The goal is not to build a fully general memory system, but to test whether structured prompting, rule retrieval, and verification can improve reliability in this controlled financial domain.

The framework will include four steps:

### 7.1 Parameter Extraction

The model first extracts the bond pricing inputs into a structured format:

* face value;
* clean price per 100 par;
* coupon rate;
* coupon frequency;
* last coupon date;
* settlement date;
* next coupon date;
* day-count convention.

### 7.2 Rule Retrieval

The relevant pricing rules are then retrieved or restated before calculation. These may include:

* clean price conversion rule;
* coupon per period rule;
* Actual/Actual rule;
* US 30/360 rule;
* dirty price formula.

### 7.3 Calculation Checklist

The model follows a fixed calculation checklist:

1. Convert clean price quoted per 100 par into dollar clean price.
2. Compute coupon per period.
3. Compute accrued fraction using the specified day-count convention.
4. Compute accrued interest.
5. Compute dirty price.
6. Validate that dirty price equals dollar clean price plus accrued interest.

### 7.4 Deterministic Verification

The final model output is compared against the Python ground-truth solver. If the output does not match, the error type is recorded.

This framework is designed to reduce errors from missing rules, forgotten conventions, and multi-document confusion.

## 8. Expected Deliverables

The expected deliverables are:

1. A focused literature survey summary on multi-document reasoning, long-context degradation, memory retention, retrieval-based memory, and LLM financial/numerical reasoning.
2. A parameterized bond pricing dataset that can generate more than 100 questions from a small number of original templates.
3. A deterministic Python solver for ground-truth bond pricing outputs.
4. A baseline experiment using simple prompts.
5. An improved experiment using the proposed structured prompting and rule-retrieval framework.
6. A comparison table showing accuracy and error types.
7. A short final report summarizing findings, limitations, and possible extensions.

## 9. Proposed Repository Structure

```text
bond-pricing-llm-memory-benchmark/
|-- README.md
|-- PROPOSAL.md
|-- LITERATURE_SURVEY.md
|-- folder1_interview_question/
|   |-- README.md
|   |-- PROMPT_COMPARISON.md
|   |-- prompts/
|   |-- src/
|   |-- data/
|   |-- results/
|-- dataset/
|   |-- templates.json
|   |-- generated_questions.json
|   |-- ground_truth.csv
|-- src/
|   |-- generate_dataset.py
|   |-- bond_pricing_solver.py
|   |-- run_experiment.py
|   |-- evaluate_outputs.py
|-- prompts/
|   |-- baseline_prompts.md
|   |-- multi_document_prompts.md
|   |-- memory_prompts.md
|   |-- framework_prompts.md
|-- results/
|   |-- baseline_results.md
|   |-- framework_results.md
|   |-- error_analysis.md
```

## 10. Tentative Summer Timeline

### Week 1: Literature Review and Project Setup

* Review relevant literature on multi-document reasoning, long-context degradation, memory retention, retrieval-based memory, and LLM financial reasoning.
* Finalize dataset templates.
* Organize the GitHub repository structure.

### Weeks 2–3: Dataset Generation and Ground Truth Solver

* Build parameterized bond pricing templates.
* Generate more than 100 test questions.
* Extend or refine the deterministic Python solver.
* Produce ground-truth outputs for all generated cases.

### Weeks 4–5: Baseline Experiments

* Run baseline prompts on selected LLMs.
* Collect model outputs.
* Compare outputs against ground truth.
* Classify common error types.

### Weeks 6–7: Solution Framework Experiments

* Implement structured prompting, rule retrieval, and calculation checklist workflows.
* Test whether the framework improves accuracy.
* Evaluate performance on single-question, multi-document, and memory-retention tasks.

### Weeks 8–9: Error Analysis and Final Report

* Summarize quantitative results.
* Analyze major failure modes.
* Compare baseline and improved framework results.
* Draft final report and prepare code walkthrough.

## 11. Scope and Limitations

This project will be scoped carefully. It does not attempt to solve LLM memory in general, nor does it claim to build a production-grade financial reasoning system.

Instead, it focuses on a controlled bond pricing benchmark where the correct answers are deterministic and where LLM failures can be measured clearly.

The main expected contribution is a small but reproducible benchmark and solution framework for evaluating whether LLMs can consistently interpret, remember, and apply bond pricing conventions across multi-document and multi-turn settings.

## 12. Current Status

An initial bond pricing prompt-engineering demo has already been created. It includes:

* deterministic ground-truth calculations;
* bad and improved prompt examples;
* comparison of initial prompts versus skill-teaching prompts;
* DeepSeek experiment results for a hard 30/360 case.

This initial work can be placed in `folder1_interview_question/` and used as the starting point for the broader summer project.
