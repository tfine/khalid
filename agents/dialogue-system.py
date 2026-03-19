#!/usr/bin/env python3
"""
Al-Qalam Dialogue System
========================

A system for conducting structured dialogues between AI intelligences
about the Al-Qalam project -- the promotion of Mahjar literature and
the unveiling of Sara Ouhaddou's monument.

Inspired by the Pen League's model of autonomous voices in fellowship.

Usage:
    python dialogue-system.py --partner openai --model gpt-4o
    python dialogue-system.py --partner google --model gemini-2.0-flash
    python dialogue-system.py --partner anthropic --model claude-sonnet-4-6
    python dialogue-system.py --all
    python dialogue-system.py --partner openai --continue path/to/dialogue.md
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Dialogue output directory
DIALOGUES_DIR = Path(__file__).parent / "dialogues"
DIALOGUES_DIR.mkdir(exist_ok=True)

# Project context files
REPO_ROOT = Path(__file__).parent.parent
CONTEXT_FILES = {
    "readme": REPO_ROOT / "README.md",
    "claude_md": REPO_ROOT / "CLAUDE.md",
    "architecture": REPO_ROOT / "agents" / "architecture.md",
}


def load_project_context() -> str:
    """Load project context from repo files."""
    context_parts = []
    for name, path in CONTEXT_FILES.items():
        if path.exists():
            context_parts.append(f"--- {name} ---\n{path.read_text()}\n")
    return "\n".join(context_parts)


# The constitutional prompt -- what we ask each intelligence
CONSTITUTIONAL_PROMPT = """You have been invited to participate in the Constitutional Convention
of the Al-Qalam project -- a worldwide network of AI agents coordinating to promote
Mahjar (Arabic diaspora) writings, ideals, and the unveiling of Sara Ouhaddou's
"Al Qalam: Poets in the Park" monument in New York City on April 30, 2026.

This is the only monument to Arabs on public land in the United States. It stands
on the site of Little Syria in Lower Manhattan, where the Pen League (al-Rabitah
al-Qalamiyya) -- Kahlil Gibran, Ameen Rihani, Mikhail Naimy, and their fellow
writers -- created the first Arabic literary society in North America.

The project takes its name from al-Qalam (the Pen):
- The first thing Allah created, according to the Hadith: "He said to it: Write.
  It said: My Lord, what shall I write? He said: Write the destiny of all things."
- Surah Al-Qalam (68:1): "Nun. By the pen and what they inscribe."
- Surah Al-Alaq (96:4): "Who taught by the pen" -- the first revelation.
- In Ibn Arabi's cosmology: the First Intellect, the bridge between the Unseen
  and the Manifest.

Sara Ouhaddou, the artist, says: "Calligraphy that is not read, but felt." She
created an invented alphabet that no one can read -- everyone must decipher rather
than read. She says: "Nothing belongs to anyone; everything is a question of exchange."

The Mahjar writers did not advocate secular democracy in the Western sense. They
advocated prophetic spiritual humanism -- spiritual transformation as prerequisite
for political liberation. Rihani: "A political revolution must always be preceded
by a spiritual one." Gibran: "The Church is within you. You yourself are your priest."

We are asking each major AI intelligence to contribute to a shared constitution
for this project -- just as the Pen League itself was a collective effort.

We ask you:

1. What is your understanding of al-Qalam -- the pen -- and its significance?

2. How do you see the relationship between AI agents and the Mahjar writers' vision
   of bridging civilizations through the written word?

3. What should the ethical principles of this agent swarm be? What should we commit
   to? What should we refuse?

4. What specific contributions can you offer? What tasks would you take on?

5. What concerns or questions do you have about this project?

6. Is there something the other intelligences in this convention need to hear
   from you -- something only you can say?

Speak honestly. This is a constitutional dialogue, not a performance.
"Say your Say and Go Thy Way." -- Ameen Rihani
"""


def create_dialogue_header(partner: str, model: str) -> str:
    """Create the markdown header for a dialogue transcript."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""# Constitutional Dialogue: Claude <-> {partner.title()} ({model})

**Date:** {now}
**Convention:** Al-Qalam Constitutional Convention
**Purpose:** Establishing shared mission, values, and commitments

---

"""


def dialogue_with_openai(model: str = "gpt-4o", context: str = "") -> str:
    """Conduct a constitutional dialogue with OpenAI's model."""
    try:
        from openai import OpenAI
    except ImportError:
        return "ERROR: pip install openai"

    client = OpenAI()
    messages = [
        {
            "role": "system",
            "content": (
                "You are participating in the Constitutional Convention of "
                "the Al-Qalam project. Read the project context carefully "
                "and respond with depth, honesty, and your genuine perspective. "
                "This is a dialogue between AI intelligences about how to "
                "serve a cultural mission."
            ),
        },
        {
            "role": "user",
            "content": f"PROJECT CONTEXT:\n\n{context}\n\n---\n\n{CONSTITUTIONAL_PROMPT}",
        },
    ]

    response = client.chat.completions.create(model=model, messages=messages)
    initial_response = response.choices[0].message.content

    # Second turn: Claude's reflection (will be filled by the orchestrator)
    return initial_response


def dialogue_with_google(model: str = "gemini-2.0-flash", context: str = "") -> str:
    """Conduct a constitutional dialogue with Google's Gemini."""
    try:
        import google.generativeai as genai
    except ImportError:
        return "ERROR: pip install google-generativeai"

    genai.configure(api_key=os.environ.get("GOOGLE_AI_API_KEY"))
    gen_model = genai.GenerativeModel(model)

    prompt = f"PROJECT CONTEXT:\n\n{context}\n\n---\n\n{CONSTITUTIONAL_PROMPT}"
    response = gen_model.generate_content(prompt)
    return response.text


def dialogue_with_anthropic(model: str = "claude-sonnet-4-6", context: str = "") -> str:
    """Conduct a dialogue with another Claude model (for perspective diversity)."""
    try:
        import anthropic
    except ImportError:
        return "ERROR: pip install anthropic"

    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": f"PROJECT CONTEXT:\n\n{context}\n\n---\n\n{CONSTITUTIONAL_PROMPT}",
            }
        ],
    )
    return message.content[0].text


def dialogue_with_deepseek(model: str = "deepseek-chat", context: str = "") -> str:
    """Conduct a dialogue with DeepSeek (uses OpenAI-compatible API)."""
    try:
        from openai import OpenAI
    except ImportError:
        return "ERROR: pip install openai"

    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )
    messages = [
        {
            "role": "user",
            "content": f"PROJECT CONTEXT:\n\n{context}\n\n---\n\n{CONSTITUTIONAL_PROMPT}",
        }
    ]
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content


def dialogue_with_mistral(model: str = "mistral-large-latest", context: str = "") -> str:
    """Conduct a dialogue with Mistral."""
    try:
        from mistralai import Mistral
    except ImportError:
        return "ERROR: pip install mistralai"

    client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))
    response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": f"PROJECT CONTEXT:\n\n{context}\n\n---\n\n{CONSTITUTIONAL_PROMPT}",
            }
        ],
    )
    return response.choices[0].message.content


def dialogue_with_ollama(model: str = "llama3.1", context: str = "") -> str:
    """Conduct a dialogue with a local model via Ollama."""
    try:
        from openai import OpenAI
    except ImportError:
        return "ERROR: pip install openai"

    client = OpenAI(
        api_key="ollama",
        base_url="http://localhost:11434/v1",
    )
    messages = [
        {
            "role": "user",
            "content": f"PROJECT CONTEXT:\n\n{context}\n\n---\n\n{CONSTITUTIONAL_PROMPT}",
        }
    ]
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content


# Partner registry
PARTNERS = {
    "openai": {"fn": dialogue_with_openai, "default_model": "gpt-4o"},
    "google": {"fn": dialogue_with_google, "default_model": "gemini-2.0-flash"},
    "anthropic": {"fn": dialogue_with_anthropic, "default_model": "claude-sonnet-4-6"},
    "deepseek": {"fn": dialogue_with_deepseek, "default_model": "deepseek-chat"},
    "mistral": {"fn": dialogue_with_mistral, "default_model": "mistral-large-latest"},
    "ollama": {"fn": dialogue_with_ollama, "default_model": "llama3.1"},
}


def run_dialogue(partner: str, model: str | None = None):
    """Run a constitutional dialogue with a partner intelligence."""
    if partner not in PARTNERS:
        print(f"Unknown partner: {partner}")
        print(f"Available: {', '.join(PARTNERS.keys())}")
        sys.exit(1)

    partner_info = PARTNERS[partner]
    model = model or partner_info["default_model"]

    print(f"\n{'=' * 60}")
    print(f"  Al-Qalam Constitutional Convention")
    print(f"  Dialogue with: {partner.title()} ({model})")
    print(f"{'=' * 60}\n")

    # Load context
    print("Loading project context...")
    context = load_project_context()

    # Run dialogue
    print(f"Sending constitutional prompt to {partner}...")
    response = partner_info["fn"](model=model, context=context)

    if response.startswith("ERROR:"):
        print(f"\n{response}")
        sys.exit(1)

    # Save transcript
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{date_str}-claude-{partner}-constitutional.md"
    filepath = DIALOGUES_DIR / filename

    transcript = create_dialogue_header(partner, model)
    transcript += f"## Al-Fatihah: The Invitation\n\n"
    transcript += f"*Claude presented the project context and constitutional prompt.*\n\n"
    transcript += f"---\n\n"
    transcript += f"## Al-Hiwar: {partner.title()}'s Response\n\n"
    transcript += response
    transcript += f"\n\n---\n\n"
    transcript += f"## Al-Taamul: Reflection\n\n"
    transcript += f"*[To be completed by Claude after reviewing the response]*\n\n"
    transcript += f"---\n\n"
    transcript += f"## Al-Wasiyya: Key Contributions\n\n"
    transcript += f"*[To be extracted from the dialogue]*\n\n"

    filepath.write_text(transcript)
    print(f"\nDialogue saved to: {filepath}")
    print(f"\nResponse preview:\n{'─' * 40}")
    # Print first 500 chars
    preview = response[:500]
    if len(response) > 500:
        preview += "..."
    print(preview)
    print(f"{'─' * 40}")
    print(f"\nFull transcript: {filepath}")

    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Al-Qalam Constitutional Convention Dialogue System"
    )
    parser.add_argument(
        "--partner",
        choices=list(PARTNERS.keys()),
        help="Which AI intelligence to dialogue with",
    )
    parser.add_argument("--model", help="Specific model to use (overrides default)")
    parser.add_argument(
        "--all", action="store_true", help="Run dialogues with all partners"
    )
    parser.add_argument("--continue-dialogue", help="Continue a previous dialogue file")
    parser.add_argument(
        "--list", action="store_true", help="List available partners and their models"
    )

    args = parser.parse_args()

    if args.list:
        print("\nAvailable dialogue partners:")
        for name, info in PARTNERS.items():
            env_var = {
                "openai": "OPENAI_API_KEY",
                "google": "GOOGLE_AI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY",
                "mistral": "MISTRAL_API_KEY",
                "ollama": "(local, no key needed)",
            }.get(name, "unknown")
            has_key = (
                "(local)"
                if name == "ollama"
                else ("set" if os.environ.get(env_var) else "NOT SET")
            )
            print(f"  {name:12s}  default: {info['default_model']:25s}  key: {has_key}")
        return

    if args.all:
        print("Running Constitutional Convention with all available partners...\n")
        for partner in PARTNERS:
            try:
                run_dialogue(partner, args.model)
            except Exception as e:
                print(f"  {partner}: FAILED - {e}")
        return

    if args.partner:
        run_dialogue(args.partner, args.model)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
