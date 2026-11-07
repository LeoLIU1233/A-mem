# Five-Slide Presentation Script

This script is written for a direct, conversational delivery. The suggested
timing totals about nine minutes.

## Slide 1 Cover

**Suggested time: 0:00 to 0:45**

Good morning. My name is Liu Yibo. This presentation reports my reproduction
of A-MEM, an agentic memory system for LLM agents.

I focused on one central claim: that Memory Evolution improves how A-MEM uses
long-term conversational memory. To test that claim, I compared the full model
with a link-only version on a small LoCoMo subset.

## Slide 2 What I Reproduced

**Suggested time: 0:45 to 2:45**

A-MEM starts by converting each conversation turn into a structured memory
note. It then retrieves similar notes, asks the language model to create links
between related memories, and uses Memory Evolution to update the context and
tags of neighboring notes.

The paper reports a clear result for GPT-4o-mini on Multi-Hop questions. Full
A-MEM reaches an F1 score of 27.02, while the version without Memory Evolution
reaches 21.35.

For my reproduction, I used the authors' benchmark code and the official
LoCoMo data. I switched to DeepSeek Chat and evaluated one conversation, its
first 120 turns, and 25 questions across five categories. I repeated the
experiment with three seeds.

Because the model and sample are smaller, my goal was to test the direction of
the claimed effect rather than to match every number in the paper.

## Slide 3 What I Changed

**Suggested time: 2:45 to 4:15**

My main scientific change was to remove Memory Evolution from the full A-MEM
pipeline.

The full model builds notes, retrieves similar memories, creates links, and
then updates the context and tags of neighboring notes.

The link-only version keeps the same note construction, retrieval, and link
generation. The only difference is that it stops the neighbor context and tag
updates.

This makes the treatment isolated. The model replacement, subset, and cache
settings are reproduction controls. The scientific change is the removal of
Memory Evolution, so the comparison measures the effect of that module.

## Slide 4 Results

**Suggested time: 4:15 to 6:45**

Across the three seeds, full A-MEM achieved an overall mean F1 of 41.76. The
link-only version achieved 38.25. That is a mean gain of 3.51 F1 points.

However, the seed-level differences were minus 0.75, plus 1.51, and plus 9.78
points. The average is positive, but one seed made the full model slightly
worse.

On Multi-Hop questions, the direction matches the paper. Full A-MEM reached
44.24, compared with 28.69 for link-only, a gain of 15.56 points.

Temporal questions did not reproduce the paper's advantage. The paper reports
45.85 for the full model and 31.24 without Memory Evolution. In my subset, the
full model reached 11.59 and link-only reached 12.62.

So the result is mixed. The Multi-Hop behavior supports the intended mechanism,
but the broad advantage claimed in the paper does not appear consistently
across all categories.

## Slide 5 Key Lessons and Next Steps

**Suggested time: 6:45 to 8:45**

The positive result is that the pipeline worked. I completed six runs, with 25
questions per run and no LLM failures. Multi-Hop improved by 15.56 points.

The limitations are also clear. Temporal changed by minus 1.03 points, and
Single-Hop changed by minus 11.43. Seed-to-seed variation is large, and the
sample has only five questions per category.

The main lesson is that reproducing an agentic system requires matching the
implementation conditions before comparing headline scores. The model, data
version, scoring convention, and retrieval parameter should be aligned first.

For future users, my recommendation is to start with a small end-to-end test,
check failures and cache state, and then expand the number of questions,
conversations, and seeds. A closer paper comparison should also use GPT-4o-mini
with the category-specific retrieval values from the paper.

In conclusion, this is a partial behavioral reproduction. The full pipeline
works, and Memory Evolution shows a useful Multi-Hop signal, but the result is
not an exact numerical replication of the paper.
