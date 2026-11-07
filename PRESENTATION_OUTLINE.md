# Five-Slide Presentation Outline

The final PDF deck is at `output/pdf/A-MEM_Reproduction_Slides.pdf`.
It is designed for a short recorded walkthrough and follows the four points
below.

## Slide 1 Cover

Introduce the project:

- A-MEM Memory Evolution Ablation;
- LIU YIBO;
- Agentic AI for Business and FinTech (FTEC5660).

## Slide 2 What I reproduced

Explain the paper's claim: Memory Evolution should improve A-MEM's use of
long-term memory. Show the paper's Multi-Hop F1 comparison:

- full A-MEM: 27.02;
- w/o ME: 21.35.

Briefly name the pipeline: note construction, retrieval, link generation, and
Memory Evolution. State the local scope: official benchmark code, official
LoCoMo data, DeepSeek Chat, one conversation, 25 questions, and three seeds.

## Slide 3 What I changed

Explain the isolated ablation:

- full A-MEM keeps neighbor context and tag updates;
- link-only A-MEM keeps note construction, retrieval, and link generation, but
  removes neighbor updates.

This is the single scientific modification. The model and subset changes are
reproduction controls.

## Slide 4 Results

Lead with the overall result:

- full mean F1: 41.76;
- link-only mean F1: 38.25;
- mean gain: 3.51 F1 points.

Show the paper-versus-local values for Multi-Hop and Temporal. State the clean
conclusion: the Multi-Hop direction reproduced, while Temporal did not.

## Slide 5 What worked and what did not

Summarize:

- the pipeline ran end to end in six runs;
- all runs evaluated 25 questions and reported zero LLM failures;
- Multi-Hop improved by 15.56 F1 points;
- Temporal changed by -1.03 and Single-Hop by -11.43;
- seed variation is large.

Close with the limitation: DeepSeek, `k=10`, one conversation, and 25
questions. The result is a partial behavioral reproduction, not an exact
numerical replication.
