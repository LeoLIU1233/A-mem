"""Summarize A-MEM evaluation JSON files with seeds and trial variance."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path


CATEGORY_NAMES = {
    1: "Multi-Hop",
    2: "Temporal",
    3: "Open-Domain",
    4: "Single-Hop",
    5: "Adversarial",
}


def load_runs(paths):
    return [
        (Path(path), json.loads(Path(path).read_text(encoding="utf-8")))
        for path in paths
    ]


def metric_mean(data, scope, metric):
    return (
        data.get("aggregate_metrics", {})
        .get(scope, {})
        .get(metric, {})
        .get("mean")
    )


def metric_count(data, scope):
    return (
        data.get("aggregate_metrics", {})
        .get(scope, {})
        .get("f1", {})
        .get("count", 0)
    )


def print_overall_table(runs):
    print("| File | Mode | Model | Seed | N | F1 | BLEU-1 |")
    print("|---|---|---|---:|---:|---:|---:|")
    for path, data in runs:
        f1 = metric_mean(data, "overall", "f1")
        bleu = metric_mean(data, "overall", "bleu1")
        f1_text = f"{100 * f1:.2f}" if f1 is not None else "n/a"
        bleu_text = f"{100 * bleu:.2f}" if bleu is not None else "n/a"
        print(
            f"| {path.name} | {data.get('memory_mode', 'unknown')} "
            f"| {data.get('model', 'unknown')} | {data.get('seed', '?')} "
            f"| {data.get('total_questions', 0)} | {f1_text} | {bleu_text} |"
        )


def print_category_table(runs):
    print("\n| Category | Mode | Seed | F1 | BLEU-1 | N |")
    print("|---|---|---:|---:|---:|---:|")
    for _, data in runs:
        mode = data.get("memory_mode", "unknown")
        seed = data.get("seed", "?")
        for category, name in CATEGORY_NAMES.items():
            scope = f"category_{category}"
            f1 = metric_mean(data, scope, "f1")
            bleu = metric_mean(data, scope, "bleu1")
            if f1 is not None and bleu is not None:
                print(
                    f"| {name} | {mode} | {seed} | {100 * f1:.2f} "
                    f"| {100 * bleu:.2f} | {metric_count(data, scope)} |"
                )


def print_variance(runs):
    grouped = defaultdict(list)
    for _, data in runs:
        f1 = metric_mean(data, "overall", "f1")
        bleu = metric_mean(data, "overall", "bleu1")
        if f1 is not None and bleu is not None:
            grouped[data.get("memory_mode", "unknown")].append((f1, bleu))

    print("\n| Mode | Trials | Mean F1 | SD F1 | Mean BLEU-1 | SD BLEU-1 |")
    print("|---|---:|---:|---:|---:|---:|")
    for mode, values in sorted(grouped.items()):
        f1_values = [100 * value[0] for value in values]
        bleu_values = [100 * value[1] for value in values]
        f1_sd = statistics.stdev(f1_values) if len(f1_values) > 1 else 0.0
        bleu_sd = statistics.stdev(bleu_values) if len(bleu_values) > 1 else 0.0
        print(
            f"| {mode} | {len(values)} | {statistics.mean(f1_values):.2f} "
            f"| {f1_sd:.2f} | {statistics.mean(bleu_values):.2f} | {bleu_sd:.2f} |"
        )

    by_seed = defaultdict(dict)
    for _, data in runs:
        by_seed[data.get("seed")][data.get("memory_mode")] = data
    paired_f1 = []
    paired_bleu = []
    print("\n| Seed | Full F1 | Link-only F1 | F1 Delta |")
    print("|---:|---:|---:|---:|")
    for seed, modes in sorted(by_seed.items()):
        if "full" not in modes or "link_only" not in modes:
            continue
        full_f1 = 100 * metric_mean(modes["full"], "overall", "f1")
        link_f1 = 100 * metric_mean(modes["link_only"], "overall", "f1")
        full_bleu = 100 * metric_mean(modes["full"], "overall", "bleu1")
        link_bleu = 100 * metric_mean(modes["link_only"], "overall", "bleu1")
        paired_f1.append(full_f1 - link_f1)
        paired_bleu.append(full_bleu - link_bleu)
        print(f"| {seed} | {full_f1:.2f} | {link_f1:.2f} | {full_f1 - link_f1:+.2f} |")

    if paired_f1:
        f1_sd = statistics.stdev(paired_f1) if len(paired_f1) > 1 else 0.0
        bleu_sd = statistics.stdev(paired_bleu) if len(paired_bleu) > 1 else 0.0
        print("\nFull minus link-only:")
        print(f"- Mean F1 delta: {statistics.mean(paired_f1):+.2f} points (SD {f1_sd:.2f})")
        print(f"- Mean BLEU-1 delta: {statistics.mean(paired_bleu):+.2f} points (SD {bleu_sd:.2f})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results", nargs="+")
    args = parser.parse_args()
    if not args.results:
        raise SystemExit("No result files supplied")
    runs = load_runs(args.results)
    print_overall_table(runs)
    print_category_table(runs)
    print_variance(runs)


if __name__ == "__main__":
    main()
