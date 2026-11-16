"""Offline tests — no API key needed (provider is mocked)."""
import json
from unittest import mock

from prompt_architect import engine

FAKE = json.dumps({
    "overall_score": 3,
    "scores": {"clarity": 4, "context": 2, "specificity": 3, "structure": 2, "output_format": 2, "examples": 1},
    "issues": ["No audience"], "assumptions": ["Blog for beginners"],
    "improved_prompt": "<role>Senior tech writer</role>", "changes": ["Added role"], "improved_score": 9,
})


def test_engineer_parses_json():
    with mock.patch.object(engine, "complete", return_value=FAKE):
        r = engine.engineer("write a blog about AI")
    assert r.overall_score == 3 and r.improved_score == 9
    assert "Senior tech writer" in r.improved_prompt
    assert "Professional Prompt" in r.to_markdown()


def test_engineer_handles_fenced_json():
    with mock.patch.object(engine, "complete", return_value="```json\n" + FAKE + "\n```"):
        assert engine.engineer("x").improved_score == 9


def test_engineer_falls_back_to_raw_text():
    with mock.patch.object(engine, "complete", return_value="Just a prompt"):
        assert engine.engineer("x").improved_prompt == "Just a prompt"
