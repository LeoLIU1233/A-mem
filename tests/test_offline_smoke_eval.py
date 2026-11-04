"""A tiny end-to-end run against a local fake OpenAI-compatible server."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import test_advanced_robust as evaluation


class _FakeOpenAIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length))
        prompt = payload["messages"][-1]["content"]

        if "Analyze the following content and provide" in prompt:
            answer = (
                "KEYWORDS: support, group, date\n"
                "CONTEXT: The speaker discusses an event and its date.\n"
                "TAGS: conversation, event, date"
            )
        elif "decide if evolution is needed" in prompt:
            answer = "DECISION: NO_EVOLUTION\nREASON: standalone note"
        elif "generate several keywords" in prompt:
            answer = "support, group, date"
        else:
            answer = "7 May 2023"

        body = json.dumps({
            "id": "local-test",
            "object": "chat.completion",
            "created": 0,
            "model": payload.get("model", "fake"),
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": answer},
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def _fake_score_prediction(prediction, qa, legacy_c5):
    return str(qa.answer), {"f1": 0.5, "bleu1": 0.25}


def _fake_aggregate_metrics(metrics, categories):
    overall = {
        name: {"mean": sum(item[name] for item in metrics) / len(metrics)}
        for name in ("f1", "bleu1")
    }
    return {"overall": overall}


def test_one_question_runs_end_to_end(tmp_path):
    dataset_source = Path(__file__).parents[1] / "data" / "locomo10.json"
    original = json.loads(dataset_source.read_text(encoding="utf-8"))
    sample = original[0]
    first_session = sample["conversation"]["session_1"]
    sample["conversation"]["session_1"] = first_session[:3]
    for key in list(sample["conversation"]):
        if key.startswith("session_") and key not in {"session_1", "session_1_date_time"}:
            del sample["conversation"][key]
    dataset = tmp_path / "tiny_locomo.json"
    dataset.write_text(json.dumps([sample]), encoding="utf-8")
    output = tmp_path / "result.json"

    server = ThreadingHTTPServer(("127.0.0.1", 0), _FakeOpenAIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base_url = f"http://127.0.0.1:{server.server_port}/v1"
        with patch.dict(
            evaluation.os.environ,
            {"OPENAI_API_KEY": "test-key", "DEEPSEEK_API_KEY": ""},
        ), patch.object(
            evaluation, "score_prediction", side_effect=_fake_score_prediction
        ), patch.object(
            evaluation, "aggregate_metrics", side_effect=_fake_aggregate_metrics
        ):
            result = evaluation.evaluate_dataset(
                str(dataset),
                model="fake-model",
                output_path=str(output),
                ratio=1.0,
                backend="openai",
                api_base=base_url,
                max_turns_per_sample=3,
                per_category=1,
                max_questions=1,
                memory_mode="none",
                seed=42,
            )
    finally:
        server.shutdown()
        thread.join(timeout=5)

    assert output.exists()
    assert result["memory_mode"] == "none"
    assert result["total_questions"] == 1
    assert result["llm_failures"] == {}
    assert result["individual_results"][0]["prediction"] == "7 May 2023"
