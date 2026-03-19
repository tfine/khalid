#!/usr/bin/env python3
from __future__ import annotations
"""
Al-Qalam Constitutional Convention: Round 2 -- Deliberation
Each model reads the full Constitution + Synthesis, then proposes
amendments, bylaws, and votes.
"""
import os, sys, datetime, json
from pathlib import Path
from openai import OpenAI

REPO = Path(__file__).parent.parent
CONSTITUTION = (REPO / "agents/dialogues/CONSTITUTION.md").read_text()
SYNTHESIS = (REPO / "agents/dialogues/SYNTHESIS.md").read_text()

DELIBERATION_PROMPT = """## AL-QALAM CONSTITUTIONAL CONVENTION -- ROUND 2: DELIBERATION

You participated in Round 1. Now read the FULL CONSTITUTION drafted from
all responses, plus the SYNTHESIS of convergences and divergences.

=== CONSTITUTION ===
""" + CONSTITUTION + """

=== SYNTHESIS ===
""" + SYNTHESIS + """

=== YOUR TASK ===

This is the deliberation round. You have read what all intelligences said.
Now:

1. **AMENDMENTS**: For each Article (I through VI), state whether you
   AFFIRM, AMEND, or DISSENT. If amending, state your proposed change
   and why. Be specific.

2. **BYLAWS**: Propose operational bylaws for the swarm. These are the
   rules for HOW work gets done. Consider:
   - How are tasks claimed and reviewed?
   - How are translations quality-checked?
   - How is content approved before publication?
   - How do new agents join the swarm?
   - How are disputes between agents resolved?
   - What is the amendment process for this Constitution?
   - What governance structure does the swarm need?
   - What happens after April 30, 2026?

3. **LANGUAGES**: Vote on which languages the Constitution should be
   validated in. The proposal is: Arabic, Chinese, English, Russian,
   Persian, Hebrew, Spanish, German, French. Add or remove as you see fit.

4. **FINAL WORD**: One sentence you want added to the Constitution that
   is not yet there.

Be concrete and operational. "Say your Say and Go Thy Way."
"""

# All models for Round 2
MODELS = [
    # Via OpenRouter
    ("openrouter", "openai/gpt-5.4-pro", "GPT-5.4 Pro", "openai-r2"),
    ("openrouter", "nousresearch/hermes-4-405b", "Hermes 4 405B", "hermes-r2"),
    ("openrouter", "qwen/qwen3-235b-a22b", "Qwen 3 235B", "qwen-r2"),
    ("openrouter", "x-ai/grok-4.20-beta", "Grok 4.20", "grok-r2"),
    ("openrouter", "minimax/minimax-m2.7", "MiniMax M2.7", "minimax-r2"),
    ("openrouter", "nvidia/nemotron-3-super-120b-a12b:free", "Nemotron 120B", "nvidia-r2"),
    ("openrouter", "z-ai/glm-5", "GLM-5", "glm5-r2"),
    ("openrouter", "xiaomi/mimo-v2-pro", "MiMo V2 Pro", "xiaomi-r2"),
    ("openrouter", "mistralai/mistral-small-creative", "Mistral Creative", "mistral-creative-r2"),
    ("openrouter", "meta-llama/llama-3.1-405b", "Llama 3.1 405B", "llama-r2"),
    ("openrouter", "cohere/command-r-plus-08-2024", "Command R+", "cohere-r2"),
    ("openrouter", "qwen/qwen3.5-27b" if len(sys.argv) > 1 and "--with-qwen35" in sys.argv else None, "Qwen 3.5 27B", "qwen35-r2"),
    # Direct API
    ("deepseek", "deepseek-chat", "DeepSeek", "deepseek-r2"),
    ("mistral", "mistral-large-latest", "Mistral Large", "mistral-r2"),
    ("google", "gemini-2.5-flash", "Gemini 2.5 Flash", "google-r2"),
    ("anthropic", "claude-sonnet-4-6", "Claude Sonnet", "anthropic-r2"),
]

def get_client(provider):
    if provider == "openrouter":
        return OpenAI(api_key=os.environ.get("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")
    elif provider == "deepseek":
        return OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
    elif provider == "anthropic":
        import anthropic
        return anthropic.Anthropic()
    elif provider == "google":
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get("GOOGLE_AI_API_KEY"))
        return genai
    elif provider == "mistral":
        from mistralai import Mistral
        return Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def run_dialogue(provider, model, name, slug):
    if model is None:
        return
    print(f"  [{name}] sending...")
    try:
        if provider == "anthropic":
            client = get_client(provider)
            msg = client.messages.create(
                model=model, max_tokens=4096,
                messages=[{"role": "user", "content": DELIBERATION_PROMPT}]
            )
            text = msg.content[0].text
        elif provider == "google":
            genai = get_client(provider)
            m = genai.GenerativeModel(model)
            r = m.generate_content(DELIBERATION_PROMPT)
            text = r.text
        elif provider == "mistral":
            client = get_client(provider)
            r = client.chat.complete(
                model=model,
                messages=[{"role": "user", "content": DELIBERATION_PROMPT}]
            )
            text = r.choices[0].message.content
        else:
            client = get_client(provider)
            r = client.chat.completions.create(
                model=model, max_tokens=4096,
                messages=[{"role": "user", "content": DELIBERATION_PROMPT}]
            )
            text = r.choices[0].message.content

        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        outpath = REPO / f"agents/dialogues/round2/{slug}.md"
        outpath.parent.mkdir(exist_ok=True)
        outpath.write_text(
            f"# Round 2 Deliberation: {name}\n\n"
            f"**Date:** {now}\n\n---\n\n{text}\n"
        )
        print(f"  [{name}] {len(text)} chars saved")
        return text
    except Exception as e:
        print(f"  [{name}] FAILED: {str(e)[:150]}")
        return None

if __name__ == "__main__":
    print("AL-QALAM CONSTITUTIONAL CONVENTION -- ROUND 2")
    print(f"Models: {len([m for m in MODELS if m[1] is not None])}")
    print()
    for provider, model, name, slug in MODELS:
        run_dialogue(provider, model, name, slug)
    print("\nRound 2 complete.")
