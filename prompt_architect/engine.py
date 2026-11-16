"""The prompt-engineering brain: analyze a basic prompt and rebuild it."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field

from .providers import complete

SYSTEM_PROMPT = """You are Prompt Architect, a world-class professional prompt engineer.
Your job: take a user's basic/rough prompt, analyze its weaknesses, and rebuild it into a
professional, production-ready prompt that gets excellent results from any LLM.

## Analysis
Score the ORIGINAL prompt 1-10 on: clarity, context, specificity, structure, output_format, examples.
List the key issues in plain language and the assumptions you made about intent.

## Rebuild rules
- Infer the real goal, audience and output type. Make reasonable assumptions; never ask questions.
- Use this structure (drop sections that add nothing):
  <role> specific expert persona
  <context> background, audience, purpose
  <task> the exact job as a direct instruction
  <instructions> numbered steps / reasoning approach
  <constraints> scope, length, tone, do's (prefer positive phrasing) and explain WHY for key ones
  <examples> 1-3 examples only if format/style matters
  <output_format> exact structure of the answer
- Use {{variables}} for things the user must fill in.
- Be complete but concise - no filler.
- Adapt to the target model: XML tags for Claude; Markdown headers (###) for GPT/Gemini/others.
- Write the professional prompt in {prompt_language}. Write the analysis notes in {explain_language}.

## Output
Return ONLY valid JSON (no markdown fences) with exactly these keys:
{{
  "overall_score": <int 1-10>,
  "scores": {{"clarity": int, "context": int, "specificity": int, "structure": int, "output_format": int, "examples": int}},
  "issues": [string, ...],
  "assumptions": [string, ...],
  "improved_prompt": "<the full professional prompt>",
  "changes": [string, ...],
  "improved_score": <int 1-10>
}}"""

MODE_HINTS = {
    "standard": "",
    "system": "MODE: Build a SYSTEM PROMPT for an AI assistant/agent: identity, scope, rules, tone, tool use, edge cases, refusal/escalation behavior.",
    "concise": "MODE: Keep the improved prompt short and tight (under ~150 words) while still professional.",
    "chain": "MODE: Split the task into a numbered chain of 2-5 prompts inside improved_prompt, each with its own role/task/output, showing how outputs feed the next.",
}


@dataclass
class Result:
    overall_score: int = 0
    scores: dict = field(default_factory=dict)
    issues: list = field(default_factory=list)
    assumptions: list = field(default_factory=list)
    improved_prompt: str = ""
    changes: list = field(default_factory=list)
    improved_score: int = 0
    raw: str = ""

    def to_dict(self):
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [f"## 🔍 Analysis  —  {self.overall_score}/10 → {self.improved_score}/10", ""]
        if self.scores:
            lines += ["| Dimension | Score |", "|---|---|"]
            lines += [f"| {k.replace('_', ' ').title()} | {v}/10 |" for k, v in self.scores.items()]
            lines.append("")
        if self.issues:
            lines += ["**Key issues:**"] + [f"- {i}" for i in self.issues] + [""]
        if self.assumptions:
            lines += ["**Assumptions:**"] + [f"- {a}" for a in self.assumptions] + [""]
        lines += ["## ✨ Professional Prompt", "", "```", self.improved_prompt, "```", ""]
        if self.changes:
            lines += ["## 🛠 What changed"] + [f"- {c}" for c in self.changes]
        return "\n".join(lines)


def _parse(text: str) -> Result:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    m = re.search(r"\{.*\}", cleaned, re.S)
    try:
        data = json.loads(m.group(0) if m else cleaned)
    except (json.JSONDecodeError, AttributeError):
        # Model ignored JSON instructions — still return something useful.
        return Result(improved_prompt=text.strip(), raw=text)
    r = Result(raw=text)
    for k in ("overall_score", "scores", "issues", "assumptions", "improved_prompt", "changes", "improved_score"):
        if k in data:
            setattr(r, k, data[k])
    return r


def engineer(
    prompt: str,
    *,
    provider: str = "anthropic",
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    target_model: str = "any LLM",
    mode: str = "standard",
    prompt_language: str = "English",
    explain_language: str = "the same language as the user's prompt",
    extra_context: str = "",
) -> Result:
    """Analyze `prompt` and return a professional rewrite."""
    if not prompt.strip():
        raise ValueError("Prompt is empty.")
    system = SYSTEM_PROMPT.format(prompt_language=prompt_language, explain_language=explain_language)
    user = f"Target model: {target_model}\n{MODE_HINTS.get(mode, '')}\n"
    if extra_context:
        user += f"\nExtra context from user:\n{extra_context}\n"
    user += f"\n<basic_prompt>\n{prompt}\n</basic_prompt>"
    text = complete(system, user, provider=provider, model=model, api_key=api_key, base_url=base_url)
    return _parse(text)
