from types import SimpleNamespace

import pytest

from reproduction_utils import parse_retrieve_k_map, select_qa_indices


def test_parse_paper_retrieval_k_configuration():
    assert parse_retrieve_k_map("1:40,2:40,3:50,4:50,5:40") == {
        1: 40,
        2: 40,
        3: 50,
        4: 50,
        5: 40,
    }


def test_category_balanced_selection_is_deterministic():
    qas = [SimpleNamespace(category=category) for category in [2, 1, 2, 3, 1, 4, 5]]
    selected = select_qa_indices(qas, per_category=1, max_questions=5)
    assert selected == [0, 1, 3, 5, 6]
    assert selected == select_qa_indices(qas, per_category=1, max_questions=5)


def test_invalid_retrieval_configuration_is_rejected():
    with pytest.raises(ValueError):
        parse_retrieve_k_map("6:10")
    with pytest.raises(ValueError):
        parse_retrieve_k_map("1")
