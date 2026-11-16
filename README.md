# ✨ Prompt Architect

**Your personal professional prompt engineer.** Paste any basic prompt → it gets analyzed, scored, and rebuilt into a professional, production-ready prompt.

Works with **Claude, GPT, Gemini, OpenRouter, Ollama (free/local)** and **any OpenAI-compatible API**. Ships as:

| | What | For whom |
|---|---|---|
| 🖥 **Web UI** | `prompt-architect ui` opens it in your browser | Everyone |
| 🧠 **Claude Skill** | `skill/prompt-architect/` | Claude.ai / Claude Code users |
| ⌨️ **CLI** | `prompt-architect "my prompt"` | Terminal users |
| 🐍 **Python library** | `from prompt_architect import engineer` | Developers |

Zero dependencies — pure Python standard library.

---

## Example

**Input:** `write a blog about AI`

**Output (shortened):**
```
Overall: 2/10 → 9/10
Issues: no audience, no length, no tone, no structure, no output format

<role>You are a senior technology writer who explains AI to non-technical readers...</role>
<context>The blog is for {{audience}} on {{website}}. Goal: ...</context>
<task>Write a {{word_count}}-word blog post about {{specific_ai_topic}}...</task>
<instructions>1. Open with a relatable hook ... </instructions>
<constraints>...</constraints>
<output_format>Markdown with H2 headings, ...</output_format>
```

---

## 🚀 Quick start (Web UI)

```bash
git clone https://github.com/jrnoorbaloch/prompt-architect.git
cd prompt-architect
pip install -e .

prompt-architect ui          # opens http://127.0.0.1:7860 in your browser
```

Click **⚙ Settings**, choose a provider, paste your API key, and go.
(No install? `python -m prompt_architect ui` also works from the repo folder.)

### Get an API key
| Provider | Key | Env variable |
|---|---|---|
| Anthropic (Claude) | console.anthropic.com | `ANTHROPIC_API_KEY` |
| OpenAI | platform.openai.com | `OPENAI_API_KEY` |
| Google Gemini | aistudio.google.com | `GEMINI_API_KEY` |
| OpenRouter | openrouter.ai | `OPENROUTER_API_KEY` |
| Ollama | none — runs locally, free | — |
| Custom (Groq, DeepSeek, LM Studio…) | provider's site | `LLM_API_KEY` + `LLM_BASE_URL` |

Keys can be entered in the UI (stored only in your browser) or set as environment variables.

---

## 🧠 Use as a Claude Skill

**Claude.ai:** zip the `skill/prompt-architect` folder → *Settings → Capabilities → Skills → Upload skill*.

```bash
cd skill && zip -r prompt-architect.zip prompt-architect
```

**Claude Code:**
```bash
cp -r skill/prompt-architect ~/.claude/skills/
```

Then just say: *"Improve this prompt: write a blog about AI"* or `/prompt-architect`.

Skill modes: default (analysis + prompt), `quick`, `system prompt`, `chain`.

---

## ⌨️ CLI

```bash
export ANTHROPIC_API_KEY=sk-ant-...
prompt-architect "make a chatbot for my shoe shop" --mode system

prompt-architect "explain recursion" -p openai -m gpt-4o --target ChatGPT
prompt-architect "write cold email" -p ollama -m llama3.1 -q > prompt.txt
echo "summarize this report" | prompt-architect -p gemini --json
```

| Flag | Meaning |
|---|---|
| `-p, --provider` | anthropic · openai · gemini · openrouter · ollama · custom |
| `-m, --model` | Model name (sensible default per provider) |
| `-t, --target` | Which model the final prompt is for (Claude, GPT…) |
| `--mode` | standard · concise · system · chain |
| `--lang` | Language of the generated prompt (English, Urdu…) |
| `--base-url` | For custom / Ollama endpoints |
| `--json` / `-q` | Raw JSON / only the final prompt |

---

## 🐍 Python

```python
from prompt_architect import engineer

r = engineer("write a blog about AI", provider="anthropic", target_model="Claude")
print(r.overall_score, "→", r.improved_score)
print(r.improved_prompt)
print(r.to_markdown())
```

---

## How it works

1. **Understands intent** — goal, audience, output type, target model.
2. **Analyzes** — scores clarity, context, specificity, structure, output format, examples (1–10).
3. **Rebuilds** with a professional template: `role → context → task → instructions → constraints → examples → output_format`, plus `{{variables}}` for reusable templates.
4. **Explains** what changed and why.

Techniques used are documented in [`skill/prompt-architect/references/techniques.md`](skill/prompt-architect/references/techniques.md).

## Project structure
```
prompt-architect/
├── prompt_architect/
│   ├── engine.py        # the prompt-engineering brain
│   ├── providers.py     # Claude / GPT / Gemini / Ollama / OpenRouter / custom
│   ├── server.py        # local web server for the UI
│   ├── cli.py           # command line
│   └── ui/index.html    # the web app
├── skill/prompt-architect/   # Claude Skill (SKILL.md + references)
├── examples/  tests/
└── pyproject.toml
```

## Run tests
```bash
pip install pytest && pytest
```

## License
MIT — free to use, modify and share.
