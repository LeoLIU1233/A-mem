"""Small, dependency-free helpers shared by the reproduction scripts."""

from typing import Dict, Iterable, List, Optional, Sequence


DEFAULT_CATEGORIES = (1, 2, 3, 4, 5)


def parse_retrieve_k_map(value: Optional[str]) -> Dict[int, int]:
    """Parse ``category:k`` pairs, e.g. ``1:40,2:40,3:50,4:50,5:40``."""
    if value is None or not value.strip():
        return {}

    result: Dict[int, int] = {}
    for pair in value.split(","):
        pieces = pair.strip().split(":")
        if len(pieces) != 2:
            raise ValueError(f"Invalid retrieval-k pair: {pair!r}")
        category, k = (int(piece.strip()) for piece in pieces)
        if category not in DEFAULT_CATEGORIES:
            raise ValueError(f"Category must be one of {DEFAULT_CATEGORIES}: {category}")
        if k <= 0:
            raise ValueError(f"Retrieval k must be positive: {k}")
        result[category] = k
    return result


def select_qa_indices(
    qas: Sequence,
    per_category: Optional[int] = None,
    max_questions: Optional[int] = None,
    allow_categories: Iterable[int] = DEFAULT_CATEGORIES,
) -> List[int]:
    """Select a deterministic, category-balanced QA subset.

    Selection keeps original question order within each category and then
    returns all chosen questions in dataset order.
    """
    allowed = tuple(allow_categories)
    eligible = [
        (qa_idx, qa) for qa_idx, qa in enumerate(qas)
        if int(qa.category) in allowed
    ]

    if per_category is None:
        selected = [qa_idx for qa_idx, _ in eligible]
    else:
        if per_category <= 0:
            raise ValueError("per_category must be positive")
        selected = []
        for category in allowed:
            category_indices = [
                qa_idx for qa_idx, qa in eligible
                if int(qa.category) == category
            ]
            selected.extend(category_indices[:per_category])
        selected = sorted(set(selected))

    if max_questions is not None:
        if max_questions <= 0:
            raise ValueError("max_questions must be positive")
        selected = selected[:max_questions]
    return selected
