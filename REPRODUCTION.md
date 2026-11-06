# A-MEM Reproduction Guide

This repository contains a runnable reproduction and a controlled ablation of
A-MEM on a LoCoMo subset. The work uses the authors' paper-evaluation code and
does not reimplement the memory system from scratch.

## Reproduction target

The target is the paper's comparison between:

- full A-MEM, with note construction, link generation, and Memory Evolution;
- A-MEM without Memory Evolution, which retains note construction and link
  generation.

The relevant paper result is Table 3 for GPT-4o-mini. The reported Multi-Hop
F1 is 27.02 for the full model and 21.35 without ME. The reported Temporal F1 is
45.85 and 31.24, respectively.

The completed local run substitutes `deepseek-chat` and evaluates a small
subset. Its results test the direction of the ablation under controlled
conditions, but they are not directly comparable with the paper's absolute
scores.

## Source code and versions

The benchmark repository baseline is:

```text
WujiangXu/AgenticMemory
commit f9a173dec325d84fcc97e7828775c7b241c33466
```

The system implementation used for reference is:

```text
agiresearch/A-mem
```

The implementation files used for evaluation include `memory_layer.py`,
`memory_layer_robust.py`, `test_advanced_robust.py`, `load_dataset.py`,
`llm_text_parsers.py`, and `utils.py`.

The LoCoMo file in `data/locomo10.json` has SHA-256:

```text
553CD5A15E25F2CECCC6ED185221EBA645080C93E5B91087560A91AA5961F365
```

It contains 10 conversations, 1,986 QA pairs, and 5,882 turns. The paper
describes 7,512 QA pairs, so the released data and paper text use different
counts.

## Environment

The completed run used Python 3.13.3 with the pinned versions in
`requirements-reproduction.txt`. A CUDA GPU is not required for the subset.

```powershell
python -m pip install -r requirements.txt
python -m pip install -r requirements-reproduction.txt
python reproduction\preflight.py
python -m pytest tests -q
```

The embedding model is `all-MiniLM-L6-v2`.

## API configuration

Create a local `.env` from `.env.example`. Do not commit the real file.

```dotenv
DEEPSEEK_API_KEY=replace-with-your-key
OPENAI_BASE_URL=https://api.deepseek.com
```

The OpenAI client uses `https://api.deepseek.com` as its base URL and
`deepseek-chat` as the model. The key is read at runtime and is not written to
result files.

## Memory modes

`full`

Builds a note, retrieves neighbors by embedding similarity, asks the LLM
whether to establish links, and updates neighbor context and tags when the
evolution decision requires it.

`link_only`

Keeps note construction, retrieval, the evolution decision, and link creation,
but skips updates to neighbor context and tags. This is the main ablation.

`none`

Skips both link generation and Memory Evolution. This mode is an auxiliary
control and is not the main modification reported in the experiment.

## Completed subset configuration

```text
dataset: data/locomo10.json
conversations: 1 of 10 (ratio 0.1)
maximum turns per conversation: 120
questions: 5 per category, 25 total
seeds: 42, 43, 44
model: deepseek-chat
retrieval k: 10 for every category
Adversarial scoring: current repository default
```

Twenty-four of the 25 selected questions have evidence within the first 120
turns. The remaining Open-Domain question has no explicit evidence identifier.

## Reproduce the completed subset

```powershell
.\reproduction\run_subset.ps1
```

The script runs full and link-only modes for all three seeds and writes:

```text
results\full_seed42.json
results\full_seed43.json
results\full_seed44.json
results\link_only_seed42.json
results\link_only_seed43.json
results\link_only_seed44.json
results\summary.md
```

Question-answering runs for seeds 43 and 44 reuse memory caches built by the
corresponding mode. Cache directories include both the mode and turn limit so
full and link-only results cannot share incompatible memories.

## Closer reproduction of the paper setting

The paper uses GPT-4o-mini and category-specific retrieval values:

```text
Multi-Hop: 40
Temporal: 40
Open-Domain: 50
Single-Hop: 50
Adversarial: 40
```

Run each mode with the full released dataset as follows:

```powershell
python test_advanced_robust.py `
  --backend openai --model gpt-4o-mini `
  --dataset data/locomo10.json `
  --retrieve_k_map "1:40,2:40,3:50,4:50,5:40" `
  --memory_mode full --legacy_c5_reference `
  --seed 42 --output results/full_paper_setting_seed42.json

python test_advanced_robust.py `
  --backend openai --model gpt-4o-mini `
  --dataset data/locomo10.json `
  --retrieve_k_map "1:40,2:40,3:50,4:50,5:40" `
  --memory_mode link_only --legacy_c5_reference `
  --seed 42 --output results/link_only_paper_setting_seed42.json
```

This is the closer setup, but the released dataset size and the current robust
evaluation path can still differ from the original paper run.

## Tests

```powershell
python -m pytest tests -q
```

The tests verify the three memory modes, DeepSeek base-URL forwarding,
category-balanced selection, retrieval-k parsing, and a one-question
end-to-end run against a local fake OpenAI-compatible server.

## Reproduction boundaries

- DeepSeek replaces GPT-4o-mini, so absolute scores should not be compared
  directly with the paper.
- The subset contains 25 questions rather than the full benchmark.
- The completed run uses `k=10`, not the paper's category-specific values.
- The remote LLM does not receive the local seed, so repeated trials remain
  stochastic. Seeds control the adversarial option order and result identity.
- The paper's Adversarial score used the legacy adversarial reference. The
  completed run uses the corrected "Not mentioned" reference.
- The paper reports no error bars for the main table.

The main result therefore concerns the direction and magnitude of the local
Memory Evolution ablation, not exact numerical agreement with Table 3.
