# A-MEM Reproduction on a LoCoMo Subset with a Memory Evolution Ablation

**Author:** Leo Liu  
**Course:** FTEC5660 Agentic AI for Business and FinTech  
**Date:** 6 November 2026  
**Repository:** https://github.com/LeoLIU1233/A-mem

## Executive summary

I reproduced the A-MEM evaluation pipeline on a 25-question LoCoMo subset and
compared full A-MEM against a version that retains link generation but removes
Memory Evolution. All six evaluation runs completed without LLM failures.
Across three seeds, full A-MEM achieved mean overall F1 of 41.76, compared with
38.25 for link-only A-MEM. The mean paired gain was 3.51 percentage points.

The result partially supports the paper's claim. Multi-Hop showed a mean F1
gain of 15.56 points. Temporal and Single-Hop did not improve, and one seed
made the full model slightly worse overall. With five questions per category
and a different model, the experiment is a behavioral reproduction rather than
an exact reproduction of the paper's numerical table.

## 1. Reproduction target

The target claim is that Memory Evolution improves A-MEM's use of long-term
conversational memory. The paper compares full A-MEM with an ablation denoted
"w/o ME" on LoCoMo. For GPT-4o-mini, the reported Multi-Hop F1 values are 27.02
and 21.35, and the Temporal F1 values are 45.85 and 31.24.

I selected this comparison because it isolates one architectural component and
has a direct, reported metric. I did not attempt to reproduce every model,
baseline, dataset, and visualization in the paper.

## 2. Implementation

I used the authors' benchmark repository instead of rebuilding the method from
the paper description. The baseline is
`WujiangXu/AgenticMemory` at commit
`f9a173dec325d84fcc97e7828775c7b241c33466`. The reference system
implementation is `agiresearch/A-mem`.

The evaluation uses the robust plain-text path in the authors' repository.
This path keeps the A-MEM sequence of note construction, embedding retrieval,
link generation, Memory Evolution, and retrieval. It avoids dependence on
OpenAI JSON Schema support.

I made one scientific modification. The `link_only` mode retains note
construction, neighbor retrieval, the LLM evolution decision, and link
creation, but skips updates to neighbor context and tags. Full mode applies
those updates. The support for DeepSeek, deterministic subset selection,
category-specific `k`, and mode-specific caches are experimental-control
changes rather than additional scientific treatments.

## 3. Data and evaluation

The completed run uses one LoCoMo conversation, its first 120 turns, and five
questions from each of the five categories. Three seeds produce 25 evaluated
questions per run. DeepSeek Chat replaces GPT-4o-mini.

The primary metrics are token-level F1 and BLEU-1. The same questions, prompts,
embedding model, turn limit, retrieval setting, and model are used for both
memory modes. Memory caches are isolated by mode and turn limit.

The released `locomo10.json` file contains 10 conversations, 1,986 QA pairs,
and 5,882 turns. Its SHA-256 begins with `553CD5A1`. The paper reports 7,512 QA
pairs, so dataset version is a material reproducibility condition.

## 4. Results

### Overall results

| Mode | Seed 42 F1 | Seed 43 F1 | Seed 44 F1 | Mean F1 | SD |
|---|---:|---:|---:|---:|---:|
| Full A-MEM | 39.68 | 43.52 | 42.10 | 41.76 | 1.94 |
| Link only, w/o ME | 40.42 | 42.01 | 32.32 | 38.25 | 5.20 |

Mean BLEU-1 was 37.83 for full A-MEM and 35.32 for link-only A-MEM. The paired
F1 differences by seed were -0.74, +1.51, and +9.78 points. The mean paired
gain of 3.51 points therefore depends substantially on seed 44.

### Category results

| Category | Full mean F1 | Link-only mean F1 | Paired gain |
|---|---:|---:|---:|
| Multi-Hop | 44.24 | 28.69 | +15.56 |
| Temporal | 11.59 | 12.62 | -1.03 |
| Open-Domain | 21.15 | 13.35 | +7.81 |
| Single-Hop | 45.17 | 56.60 | -11.43 |
| Adversarial | 86.67 | 80.00 | +6.67 |

The Multi-Hop result is consistent with the intended mechanism: links and
updated neighbor descriptions can surface evidence across different dialogue
sessions. The result is still unstable, with a standard deviation of 16.78 for
the paired Multi-Hop difference.

Temporal does not reproduce the paper's large advantage. Single-Hop is better
without Memory Evolution in this subset. A plausible explanation is that
single-hop answers already have a close semantic match, while evolution adds
context that can dilute short answers. This explanation is provisional because
the subset is small.

## 5. What reproduced

The execution pipeline reproduced successfully. All six result files contain
the expected 25 questions, all LLM failure counters are empty, and the cache
transition from seed 42 to seeds 43 and 44 behaves as designed. Twenty-four of
the 25 questions have evidence inside the supplied 120 turns.

The experiment also reproduces the expected directional benefit of Memory
Evolution on Multi-Hop and on the overall mean. It does not reproduce a
consistent benefit on every category.

## 6. Limitations

The absolute scores cannot be compared with the paper. DeepSeek Chat differs
from GPT-4o-mini, the sample is smaller, and the completed run uses retrieval
`k=10` rather than 40/40/50/50/40.

The current Adversarial score uses the repository's corrected "Not mentioned"
reference. The paper used the legacy adversarial-answer reference. This change
improves scoring logic but prevents a like-for-like comparison with the
reported Adversarial number.

The remote model does not receive the local seed. Repeated seeds therefore test
run-to-run variability as well as adversarial option ordering. With five
questions per category, one question changes a category score by 20 points.

Finally, the result is limited to one conversation. The subset now gives a
useful pilot, but a stronger claim requires more conversations and more
questions per category.

## 7. Debugging record

The first repository identified in the task was the system implementation
repository. Its README directs benchmark reproduction to
`WujiangXu/AgenticMemory`, so I switched to the benchmark repository and its
LoCoMo data.

The original evaluation expects structured JSON output from an OpenAI model.
I used the repository's robust plain-text path to support DeepSeek. The
existing script did not expose the paper's category-specific retrieval
settings, so I added a `--retrieve_k_map` option.

Initial tests used a local fake OpenAI-compatible server. They verified memory
construction, query generation, answer generation, result serialization,
mode-specific behavior, and cache paths without spending API credits. The final
six runs then used DeepSeek Chat.

The dataset counts, model identity, prompt templates, missing API calls, and
invalid links are logged or stored in the result JSON. API keys, memory caches,
and verbose logs are excluded from version control.

## 8. Conclusion

The A-MEM comparison is reproducible at the pipeline level, and the local
ablation gives a positive overall signal for Memory Evolution. The strongest
support comes from Multi-Hop. The paper's advantage does not transfer
consistently to Temporal or Single-Hop under the small DeepSeek subset.

Future work should repeat the same subset with more seeds, expand to more
questions and conversations, and run the paper-aligned GPT-4o-mini setting with
category-specific retrieval values. Those changes are necessary before making
an exact numerical reproducibility claim.
