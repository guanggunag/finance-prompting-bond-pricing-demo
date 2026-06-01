# Literature Survey: LLM Multi-Document Reasoning and Memory Retention for Bond Pricing Tasks

## 1. Purpose of This Literature Survey

This document is a working literature survey for the summer project proposal.

The project studies two LLM reliability problems in a controlled finance setting:

1. LLMs may misinterpret information when multiple documents are provided.
2. LLMs may forget or inconsistently apply facts and rules over a long interaction.

The finance domain used in this project is bond pricing. The goal is not simply to test whether an LLM can calculate a simple bond price. Instead, bond pricing is used as a controlled benchmark because it has deterministic ground truth and convention-sensitive calculations.

The literature survey will focus on research related to:

* multi-document reasoning;
* long-context reasoning and context degradation;
* memory retention across multi-turn interactions;
* retrieval-augmented generation and external memory;
* numerical and financial reasoning by LLMs.

This file is intentionally conservative. It does not include unverified paper titles or invented citations. Additional papers and notes will be added after further review.

## 2. Connection to the Bond Pricing Project

Bond pricing is a useful test domain because many errors come from misinterpreting or forgetting specific rules rather than from difficult arithmetic alone.

Examples include:

* treating a clean price quoted per 100 par as a total dollar price;
* using the annual coupon instead of coupon per period;
* forgetting the coupon frequency;
* mixing Actual/Actual and 30/360 day-count conventions;
* applying a general rule when a bond-specific term should override it;
* forgetting a previously stated convention after several follow-up questions.

These failure modes map naturally to the LLM research directions in this project:

| LLM Reliability Problem  | Bond Pricing Example                                                         |
| ------------------------ | ---------------------------------------------------------------------------- |
| Multi-document confusion | The model uses the day-count convention from the wrong document.             |
| Long-context degradation | The relevant convention is stated early in the prompt but ignored later.     |
| Memory loss over time    | The model forgets that all clean prices are quoted per 100 par.              |
| Weak verification        | The model gives a plausible dirty price but does not check accrued interest. |
| Rule conflict            | The model follows a general rule instead of a specific bond term.            |

## 3. Literature Area 1: Multi-Document Reasoning

### 3.1 Why This Area Matters

When multiple documents are given to an LLM, the model may need to identify which document contains the relevant information, ignore irrelevant text, and synthesize the answer without mixing facts across documents.

For bond pricing, this matters because a pricing task may provide:

* one document with general bond pricing formulas;
* one document with bond-specific terms;
* one document with day-count convention definitions;
* one document with examples that may be irrelevant to the target bond.

The model must select and apply the correct information.

### 3.2 Confirmed Relevant Work

#### Lost in the Middle: How Language Models Use Long Contexts

This paper studies how language models use information in long input contexts. It evaluates tasks that include multi-document question answering and key-value retrieval. A key finding is that performance can degrade depending on where the relevant information appears in the context, with models often performing better when relevant information appears near the beginning or end rather than in the middle.

Relevance to this project:

* The bond pricing benchmark can vary the position of the relevant convention or bond term across multiple documents.
* The experiment can test whether LLMs fail when the key pricing rule is placed in the middle of the prompt.
* This paper supports the idea that long context availability does not guarantee reliable use of all context.

Citation to add later:

* Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, Percy Liang. “Lost in the Middle: How Language Models Use Long Contexts.” 2023.

### 3.3 How This Literature Informs the Project

The project can include multi-document bond pricing cases where the relevant rule appears in different document positions:

* beginning;
* middle;
* end.

The experiment can then compare whether model accuracy changes when the same information is moved to a different location.

## 4. Literature Area 2: Long-Context Reasoning and Context Degradation

### 4.1 Why This Area Matters

LLMs may support long context windows, but this does not necessarily mean that they reliably use every part of the context. Long-context tasks can involve retrieval, reasoning, summarization, and consistency across many tokens.

For bond pricing, long-context failure may appear when the model ignores an earlier rule such as:

* “All clean prices are quoted per 100 par.”
* “Use US 30/360 when the day-count convention is 30/360.”
* “Always compute coupon per period before accrued interest.”

### 4.2 Confirmed Relevant Work

#### LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding

LongBench is a benchmark for evaluating long-context understanding. It includes task categories such as single-document QA, multi-document QA, summarization, few-shot learning, synthetic tasks, and code completion.

Relevance to this project:

* LongBench provides an example of how to structure a benchmark for long-context understanding.
* The bond pricing project can follow the same general idea of standardized tasks and automatic evaluation, but in a narrower finance-specific setting.
* The project can adapt the benchmark philosophy to deterministic financial calculations.

Citation to add later:

* Yushi Bai et al. “LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding.” 2023.

### 4.3 How This Literature Informs the Project

The project can design tests where the relevant pricing rule is placed far from the final question, or where the model must maintain the same rule across a long sequence of related questions.

Possible experiment design:

1. Provide a rule document at the beginning.
2. Provide several distractor examples.
3. Ask a bond pricing question at the end.
4. Check whether the model still applies the original rule correctly.

## 5. Literature Area 3: Memory Retention Across Multi-Turn Interactions

### 5.1 Why This Area Matters

The advisor specifically mentioned memory over time as a research direction. The examples were:

* facts given on Monday may be forgotten by Wednesday;
* facts may be forgotten after 10–15 queries.

In this project, memory retention is studied in a controlled way. The model is given a pricing convention or session-level rule early in the conversation, then asked multiple bond pricing questions later.

### 5.2 Confirmed Relevant Work

#### MemGPT: Towards LLMs as Operating Systems

MemGPT proposes a virtual context management approach for LLMs. The system manages different memory tiers so that a model can work with information beyond its limited context window. It is evaluated in domains including document analysis and multi-session chat.

Relevance to this project:

* MemGPT is relevant to the idea that long-term memory requires explicit management rather than relying only on the current prompt.
* The bond pricing project can test a simpler version of this idea by using structured memory summaries or rule stores.
* The project does not aim to implement a full MemGPT-style system, but the paper helps motivate memory management as an explicit design problem.

Citation to add later:

* Charles Packer, Sarah Wooders, Kevin Lin, Vivian Fang, Shishir G. Patil, Ion Stoica, Joseph E. Gonzalez. “MemGPT: Towards LLMs as Operating Systems.” 2023.

### 5.3 How This Literature Informs the Project

The project can use a simple memory framework instead of a complex memory system:

* maintain a short rule summary;
* restate applicable pricing rules before each calculation;
* retrieve the relevant convention from a rule file;
* verify calculations against a deterministic solver.

This keeps the scope manageable while still addressing the advisor’s memory-retention direction.

## 6. Literature Area 4: Retrieval-Augmented Generation and External Memory

### 6.1 Why This Area Matters

Retrieval-augmented generation is relevant because one possible solution to memory failure is not to rely only on the model’s internal memory. Instead, the model can retrieve the relevant rule or document at the time of the question.

For bond pricing, this means the model can retrieve:

* clean price conversion rules;
* coupon per period formula;
* Actual/Actual convention;
* US 30/360 convention;
* dirty price validation formula.

### 6.2 Confirmed Relevant Work

#### Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

The original RAG work combines parametric model memory with a non-parametric external memory accessed through retrieval. The paper motivates retrieval as a way to improve factuality, specificity, and access to external knowledge.

Relevance to this project:

* The bond pricing framework can use a small rule library as external memory.
* Instead of expecting the model to remember every convention, the model can retrieve the relevant rule before calculation.
* The project can compare baseline prompting with rule-retrieval prompting.

Citation to add later:

* Patrick Lewis et al. “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.” 2020.

#### Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection

Self-RAG studies retrieval, generation, and critique through self-reflection. It is relevant because the project’s proposed framework includes a verification step after generation.

Relevance to this project:

* The bond pricing framework can require the model to decide which rule is needed, apply the rule, and then check the final answer.
* The project can borrow the idea that generation should be paired with critique or verification.
* The implementation here will remain simpler than Self-RAG and will focus on prompt-level rule retrieval and deterministic checking.

Citation to add later:

* Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, Hannaneh Hajishirzi. “Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection.” 2023.

### 6.3 How This Literature Informs the Project

The solution framework can include:

1. retrieve relevant rule;
2. extract parameters;
3. calculate using a checklist;
4. verify with deterministic solver.

This is a practical and limited version of retrieval-augmented reasoning for a finance calculation task.

## 7. Literature Area 5: Reasoning, Acting, and Tool Use

### 7.1 Why This Area Matters

In finance tasks, a model may need to do more than produce text. It may need to extract parameters, call tools, run calculations, and verify outputs.

### 7.2 Confirmed Relevant Work

#### ReAct: Synergizing Reasoning and Acting in Language Models

ReAct combines reasoning traces with actions such as interacting with tools or external sources. It is relevant because the bond pricing framework can be viewed as a small tool-assisted reasoning pipeline.

Relevance to this project:

* The model can reason about which pricing rule applies.
* It can use an external solver or rule file.
* It can verify whether the final dirty price matches the deterministic calculation.
* The project can use this as motivation for a simple agentic workflow without claiming to build a full agent system.

Citation to add later:

* Shunyu Yao et al. “ReAct: Synergizing Reasoning and Acting in Language Models.” 2022.

### 7.3 How This Literature Informs the Project

A possible workflow is:

1. Read the documents.
2. Identify relevant bond terms.
3. Retrieve applicable pricing rules.
4. Compute the answer.
5. Check the answer with a deterministic solver.
6. Record the error type if the answer is wrong.

This is a lightweight reasoning-and-tool-use workflow.

## 8. Literature Area 6: Numerical and Financial Reasoning

### 8.1 Why This Area Matters

Bond pricing requires both financial convention interpretation and numerical reasoning. LLMs may write convincing explanations but still make numerical or convention errors.

### 8.2 Confirmed Relevant Work

#### ConvFinQA: Exploring the Chain of Numerical Reasoning in Conversational Finance Question Answering

ConvFinQA studies numerical reasoning in conversational finance question answering. It focuses on real-world financial reasoning paths in a conversational setting.

Relevance to this project:

* The bond pricing project also involves financial numerical reasoning.
* The memory-retention tasks are conversational and multi-turn.
* The project can use ConvFinQA as motivation for studying finance-specific reasoning rather than general arithmetic only.

Citation to add later:

* Zhiyu Chen, Shiyang Li, Charese Smiley, Zhiqiang Ma, Sameena Shah, William Yang Wang. “ConvFinQA: Exploring the Chain of Numerical Reasoning in Conversational Finance Question Answering.” 2022.

#### FinBen: A Holistic Financial Benchmark for Large Language Models

FinBen is a broader financial benchmark for LLMs. It covers multiple financial task types, including information extraction, question answering, text generation, risk management, forecasting, decision-making, agent evaluation, and RAG evaluation.

Relevance to this project:

* FinBen shows the importance of finance-specific evaluation.
* The proposed bond pricing benchmark is narrower, but it offers deterministic ground truth and convention-sensitive error analysis.
* This project can be positioned as a small specialized benchmark rather than a broad financial benchmark.

Citation to add later:

* Qianqian Xie et al. “FinBen: A Holistic Financial Benchmark for Large Language Models.” 2024.

## 9. Proposed Literature Survey Summary Table

| Area                                    | Paper / Resource   | Main Idea                                                                        | Use in This Project                                                                                   |
| --------------------------------------- | ------------------ | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Multi-document / long-context reasoning | Lost in the Middle | Models may not use long context robustly; relevant information position matters. | Test whether bond pricing accuracy changes when the key rule appears in different document positions. |
| Long-context benchmark design           | LongBench          | Benchmark for long-context understanding across multiple task categories.        | Use standardized task generation and automatic evaluation ideas in a finance-specific benchmark.      |
| Memory management                       | MemGPT             | Explicit memory management for long documents and multi-session chat.            | Motivate simple rule memory or summary memory for bond pricing conventions.                           |
| Retrieval-augmented generation          | RAG                | Retrieve external knowledge instead of relying only on parametric memory.        | Retrieve bond pricing rules before calculation.                                                       |
| Retrieval + critique                    | Self-RAG           | Combine retrieval, generation, and critique.                                     | Add a verification step after model calculation.                                                      |
| Reasoning + tool use                    | ReAct              | Combine reasoning with actions/tools.                                            | Use a lightweight workflow: extract, retrieve, compute, verify.                                       |
| Financial numerical reasoning           | ConvFinQA          | Conversational financial numerical reasoning benchmark.                          | Motivate multi-turn finance-specific reasoning tests.                                                 |
| Financial LLM benchmark                 | FinBen             | Broad benchmark for financial LLM evaluation.                                    | Position this project as a smaller deterministic bond-pricing benchmark.                              |

## 10. Open Questions for Advisor Feedback

The current survey suggests several possible directions. I would like advisor feedback on the following:

1. Should the project focus more on multi-document interpretation or memory retention?
2. Should the benchmark use mostly structured JSON-style inputs, natural-language mini term sheets, or both?
3. Should the first version focus only on clean-to-dirty price conversion, or should yield-based pricing also be included?
4. Should the solution framework remain prompt-based, or should it include a simple retrieval component?
5. Which LLMs should be tested first?
6. How extensive should the literature survey be for the summer project?

## 11. Current Status and Next Steps

Current status:

* An initial bond pricing prompt demo has been created.
* A deterministic solver exists for clean price, accrued interest, and dirty price.
* Initial bad and improved prompts have been compared.
* A separate prompt comparison file explains the skill taught by the improved prompts.

Next steps:

1. Expand the literature survey with verified citations and short summaries.
2. Finalize the benchmark templates.
3. Generate 100+ parameterized bond pricing questions.
4. Design multi-document and memory-retention task variants.
5. Run baseline LLM experiments.
6. Test whether structured prompting, rule retrieval, and verification improve reliability.

## 12. References To Be Completed

The following references have been identified as relevant and should be verified and formatted consistently before final submission:

* Liu et al. “Lost in the Middle: How Language Models Use Long Contexts.” 2023.
* Bai et al. “LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding.” 2023.
* Packer et al. “MemGPT: Towards LLMs as Operating Systems.” 2023.
* Lewis et al. “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.” 2020.
* Asai et al. “Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection.” 2023.
* Yao et al. “ReAct: Synergizing Reasoning and Acting in Language Models.” 2022.
* Chen et al. “ConvFinQA: Exploring the Chain of Numerical Reasoning in Conversational Finance Question Answering.” 2022.
* Xie et al. “FinBen: A Holistic Financial Benchmark for Large Language Models.” 2024.
