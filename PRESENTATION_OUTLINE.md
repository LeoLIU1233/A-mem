# Presentation Outline for A-MEM Reproduction

This outline supports a 12-minute recorded presentation. The video itself is
not part of this repository.

## Slide 1 Project and claim

State the paper, repository, and target:

- A-MEM: Agentic Memory for LLM Agents;
- paper benchmark repository WujiangXu/AgenticMemory;
- target: full A-MEM versus w/o Memory Evolution on LoCoMo.

Use the paper's GPT-4o-mini Multi-Hop result as the reference: F1 27.02 versus
21.35.

## Slide 2 Memory pipeline

Explain the four stages:

1. note construction with content, time, keywords, context, tags, and embedding;
2. embedding-based neighbor retrieval;
3. LLM-driven link generation;
4. Memory Evolution through updates to neighbor context and tags.

State the mechanism claim: links and evolved descriptions should help retrieve
and connect evidence across dialogue sessions.

## Slide 3 Reproduction scope

Show the completed settings in a small table:

- deepseek-chat;
- one LoCoMo conversation;
- first 120 turns;
- five questions per category;
- seeds 42, 43, and 44;
- retrieval k=10.

Make clear that these conditions support a behavioral test, not an exact copy
of the paper's full GPT-4o-mini experiment.

## Slide 4 Modification

Show the isolated treatment:

- full: link generation and neighbor updates;
- link_only: link generation without neighbor updates;
- none: no links and no evolution.

Explain that `none` is a control. The reported modification is full versus
link-only.

## Slide 5 Execution quality

Report:

- six completed result files;
- 25 questions per run;
- zero LLM failures;
- isolated caches by memory mode;
- 24 of 25 questions with evidence inside the supplied turns.

This establishes that the comparison was executable and controlled.

## Slide 6 Overall results

Show:

| Mode | Mean F1 | SD | Mean BLEU-1 |
|---|---:|---:|---:|
| Full A-MEM | 41.76 | 1.94 | 37.83 |
| Link only | 38.25 | 5.20 | 35.32 |

The mean F1 gain is 3.51 points. Mention that the paired seed differences are
-0.75, +1.51, and +9.78.

## Slide 7 Category results

Show the paired F1 gains:

| Category | Gain |
|---|---:|
| Multi-Hop | +15.56 |
| Temporal | -1.03 |
| Open-Domain | +7.81 |
| Single-Hop | -11.43 |
| Adversarial | +6.67 |

Emphasize the Multi-Hop result and the large seed variation.

## Slide 8 What reproduced

Say that the pipeline and the Multi-Hop behavioral direction reproduced. The
overall mean is positive. The paper's broad advantage did not reproduce
consistently across categories.

Avoid claiming that 41.76 reproduces a paper number. It does not.

## Slide 9 Limitations

Cover:

- DeepSeek instead of GPT-4o-mini;
- one conversation and 25 questions;
- k=10 instead of the paper's category-specific values;
- corrected Adversarial scoring versus the paper's legacy reference;
- remote model randomness across seeds;
- released data count differs from the paper's stated QA count.

## Slide 10 Conclusions and next steps

Conclude that Memory Evolution has a plausible Multi-Hop benefit but the
evidence is not stable enough to generalize. The next test should use a larger
subset, more seeds, and the paper-aligned model and retrieval values.
