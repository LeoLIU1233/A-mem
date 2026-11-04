from types import SimpleNamespace
from unittest.mock import patch

import memory_layer_robust as robust
from memory_layer_robust import RobustAgenticMemorySystem, RobustMemoryNote


class FakeLLM:
    def __init__(self):
        self.prompts = []

    def get_completion(self, prompt, temperature=0.7):
        self.prompts.append(prompt)
        if "decide if evolution is needed" in prompt:
            return "DECISION: STRENGTHEN_AND_UPDATE\nREASON: related memory"
        if "Which neighbor indices" in prompt:
            return "CONNECTIONS: 0\nTAGS: updated-new-memory"
        if "For each neighbor" in prompt:
            return "NEIGHBOR 0:\nCONTEXT: updated merged context\nTAGS: updated-neighbor"
        raise AssertionError(f"Unexpected prompt: {prompt[:100]}")


def make_system(mode):
    neighbor = RobustMemoryNote(
        content="Neighbor memory about a morning run.",
        id="neighbor",
        keywords=["run", "morning"],
        context="An old context",
        tags=["exercise"],
        timestamp="202501010900",
    )
    system = RobustAgenticMemorySystem.__new__(RobustAgenticMemorySystem)
    system.memories = {neighbor.id: neighbor}
    system.refresh_index = False
    system.memory_mode = mode
    system.llm_controller = SimpleNamespace(llm=FakeLLM())
    system.find_related_memories = lambda query, k=5: (
        "memory index:0 neighbor",
        [0],
    )
    return system, neighbor


def run_mode(mode):
    system, neighbor = make_system(mode)
    note = RobustMemoryNote(
        content="A new memory about running before breakfast.",
        id="new",
        keywords=["running", "breakfast"],
        context="A new context",
        tags=["exercise"],
        timestamp="202501020900",
    )
    changed, result = system.process_memory(note)
    return system, neighbor, changed, result


def test_full_mode_links_and_updates_neighbor():
    system, neighbor, changed, note = run_mode("full")
    assert changed is True
    assert note.links == [0]
    assert neighbor.context == "updated merged context"
    assert neighbor.tags == ["updated-neighbor"]
    assert len(system.llm_controller.llm.prompts) == 3


def test_link_only_mode_keeps_neighbor_unchanged():
    system, neighbor, changed, note = run_mode("link_only")
    assert changed is True
    assert note.links == [0]
    assert neighbor.context == "An old context"
    assert neighbor.tags == ["exercise"]
    assert len(system.llm_controller.llm.prompts) == 2


def test_none_mode_disables_link_generation_and_evolution():
    system, neighbor, changed, note = run_mode("none")
    assert changed is False
    assert note.links == []
    assert neighbor.context == "An old context"
    assert neighbor.tags == ["exercise"]
    assert system.llm_controller.llm.prompts == []


def test_deepseek_api_base_is_forwarded_without_committing_secret():
    def fake_getenv(name):
        return {"DEEPSEEK_API_KEY": "test-secret"}.get(name)

    with patch.object(robust.os, "getenv", side_effect=fake_getenv), patch(
        "openai.OpenAI"
    ) as openai_client:
        robust.RobustOpenAIController(
            model="deepseek-chat",
            api_base="https://api.deepseek.com",
        )
    openai_client.assert_called_once_with(
        api_key="test-secret",
        base_url="https://api.deepseek.com",
    )
