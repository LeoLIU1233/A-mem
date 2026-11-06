| File | Mode | Model | Seed | N | F1 | BLEU-1 |
|---|---|---|---:|---:|---:|---:|
| full_seed42.json | full | deepseek-chat | 42 | 25 | 39.68 | 35.21 |
| full_seed43.json | full | deepseek-chat | 43 | 25 | 43.52 | 39.23 |
| full_seed44.json | full | deepseek-chat | 44 | 25 | 42.10 | 39.06 |
| link_only_seed42.json | link_only | deepseek-chat | 42 | 25 | 40.42 | 36.74 |
| link_only_seed43.json | link_only | deepseek-chat | 43 | 25 | 42.01 | 38.85 |
| link_only_seed44.json | link_only | deepseek-chat | 44 | 25 | 32.32 | 30.36 |

| Category | Mode | Seed | F1 | BLEU-1 | N |
|---|---|---:|---:|---:|---:|
| Multi-Hop | full | 42 | 44.24 | 34.44 | 5 |
| Temporal | full | 42 | 16.43 | 9.35 | 5 |
| Open-Domain | full | 42 | 12.53 | 8.07 | 5 |
| Single-Hop | full | 42 | 45.17 | 44.19 | 5 |
| Adversarial | full | 42 | 80.00 | 80.00 | 5 |
| Multi-Hop | full | 43 | 44.24 | 34.44 | 5 |
| Temporal | full | 43 | 13.33 | 9.10 | 5 |
| Open-Domain | full | 43 | 34.86 | 28.42 | 5 |
| Single-Hop | full | 43 | 45.17 | 44.19 | 5 |
| Adversarial | full | 43 | 80.00 | 80.00 | 5 |
| Multi-Hop | full | 44 | 44.24 | 34.44 | 5 |
| Temporal | full | 44 | 5.00 | 1.35 | 5 |
| Open-Domain | full | 44 | 16.06 | 15.31 | 5 |
| Single-Hop | full | 44 | 45.17 | 44.19 | 5 |
| Adversarial | full | 44 | 100.00 | 100.00 | 5 |
| Multi-Hop | link_only | 42 | 30.91 | 27.09 | 5 |
| Temporal | link_only | 42 | 16.43 | 9.35 | 5 |
| Open-Domain | link_only | 42 | 12.45 | 8.08 | 5 |
| Single-Hop | link_only | 42 | 62.32 | 59.19 | 5 |
| Adversarial | link_only | 42 | 80.00 | 80.00 | 5 |
| Multi-Hop | link_only | 43 | 44.24 | 34.44 | 5 |
| Temporal | link_only | 43 | 10.71 | 7.07 | 5 |
| Open-Domain | link_only | 43 | 12.79 | 13.53 | 5 |
| Single-Hop | link_only | 43 | 62.32 | 59.19 | 5 |
| Adversarial | link_only | 43 | 80.00 | 80.00 | 5 |
| Multi-Hop | link_only | 44 | 10.91 | 7.09 | 5 |
| Temporal | link_only | 44 | 10.71 | 7.07 | 5 |
| Open-Domain | link_only | 44 | 14.81 | 13.46 | 5 |
| Single-Hop | link_only | 44 | 45.17 | 44.19 | 5 |
| Adversarial | link_only | 44 | 80.00 | 80.00 | 5 |

| Mode | Trials | Mean F1 | SD F1 | Mean BLEU-1 | SD BLEU-1 |
|---|---:|---:|---:|---:|---:|
| full | 3 | 41.76 | 1.94 | 37.83 | 2.27 |
| link_only | 3 | 38.25 | 5.20 | 35.32 | 4.42 |

| Seed | Full F1 | Link-only F1 | F1 Delta |
|---:|---:|---:|---:|
| 42 | 39.68 | 40.42 | -0.75 |
| 43 | 43.52 | 42.01 | +1.51 |
| 44 | 42.10 | 32.32 | +9.78 |

Full minus link-only:
- Mean F1 delta: +3.51 points (SD 5.54)
- Mean BLEU-1 delta: +2.52 points (SD 5.44)
