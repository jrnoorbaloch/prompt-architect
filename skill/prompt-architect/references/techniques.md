# Prompt Engineering Techniques — Reference

Use the ones that fit the task. Don't apply all blindly.

## Core
1. **Role prompting** — "You are a senior tax accountant with 15 years of experience in…" Specific beats generic.
2. **Context first** — who the audience is, why the task exists, what success looks like.
3. **Direct instructions** — imperative verbs: "Write", "List", "Compare".
4. **Explicit output format** — headings, JSON schema, word count, bullet vs prose.
5. **Positive framing** — "Write in flowing paragraphs" instead of "Don't use bullets".
6. **Explain the why** — "Keep it under 100 words because it will be shown on a mobile notification."

## Structure
7. **XML / Markdown sections** — separate instructions, context, data, examples.
8. **Variables** — `{{customer_name}}`, `{{document}}` for reusable templates.
9. **Long data on top, question at the bottom** — for long documents, put the material first.

## Reasoning
10. **Step-by-step** — "Think through this step by step before answering" for analysis, math, logic.
11. **Plan → execute** — ask for an outline before the full output on long tasks.
12. **Self-check** — "Before finishing, verify the answer against the constraints above."

## Examples
13. **Few-shot** — 1–3 diverse examples wrapped in `<example>` tags; show edge cases.
14. **Contrastive** — a good and a bad example when quality is subjective.

## Reliability
15. **Grounding** — "Only use information from the provided document; if it isn't there, say so."
16. **Uncertainty permission** — "If you're unsure, say 'I don't know' instead of guessing."
17. **Prefill / format lock** — start the answer with `{` for JSON (API use).

## Agents / system prompts
18. Identity & scope, tools available, decision rules, tone, escalation/refusal rules, edge cases.

## Model notes
- **Claude** — XML tags, detailed context, explain reasons; responds well to precise instructions.
- **GPT** — Markdown sections, clear delimiters (`"""`, `###`).
- **Gemini** — clear task + format; put the instruction after long context.
- **Small/open models (Llama, Mistral)** — shorter prompts, very explicit format, examples help a lot.
