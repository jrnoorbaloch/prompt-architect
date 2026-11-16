"""Command line interface.

  prompt-architect ui                         # open the web UI
  prompt-architect "write a blog about AI"    # improve a prompt in terminal
  echo "my prompt" | prompt-architect -p openai --json
"""
from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .engine import engineer
from .providers import DEFAULT_MODELS, ProviderError


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] == "ui":
        ap = argparse.ArgumentParser(prog="prompt-architect ui")
        ap.add_argument("--host", default="127.0.0.1")
        ap.add_argument("--port", type=int, default=7860)
        ap.add_argument("--no-browser", action="store_true")
        a = ap.parse_args(argv[1:])
        from .server import serve
        return serve(a.host, a.port, not a.no_browser)

    ap = argparse.ArgumentParser(prog="prompt-architect", description="Turn basic prompts into professional prompts.")
    ap.add_argument("prompt", nargs="?", help="Basic prompt (or pipe via stdin). Use 'ui' to open the web app.")
    ap.add_argument("-p", "--provider", default="anthropic", choices=list(DEFAULT_MODELS))
    ap.add_argument("-m", "--model", help="Model name (defaults per provider)")
    ap.add_argument("--base-url", help="For custom/ollama OpenAI-compatible endpoints")
    ap.add_argument("--api-key", help="API key (else read from env)")
    ap.add_argument("-t", "--target", default="any LLM", help="Model the final prompt is for, e.g. Claude, GPT")
    ap.add_argument("--mode", default="standard", choices=["standard", "system", "concise", "chain"])
    ap.add_argument("--lang", default="English", help="Language of the generated prompt")
    ap.add_argument("--json", action="store_true", help="Output raw JSON")
    ap.add_argument("-q", "--quiet", action="store_true", help="Print only the improved prompt")
    ap.add_argument("-V", "--version", action="version", version=__version__)
    a = ap.parse_args(argv)

    prompt = a.prompt if a.prompt else (sys.stdin.read() if not sys.stdin.isatty() else "")
    if not prompt.strip():
        ap.print_help()
        return 1
    try:
        res = engineer(prompt, provider=a.provider, model=a.model, api_key=a.api_key, base_url=a.base_url,
                       target_model=a.target, mode=a.mode, prompt_language=a.lang)
    except (ProviderError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    if a.json:
        d = res.to_dict(); d.pop("raw", None)
        print(json.dumps(d, indent=2, ensure_ascii=False))
    elif a.quiet:
        print(res.improved_prompt)
    else:
        print(res.to_markdown())
    return 0


if __name__ == "__main__":
    sys.exit(main())
