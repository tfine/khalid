#!/usr/bin/env python3
from __future__ import annotations
"""
Al-Majlis: The Deliberation Engine
===================================

Orchestrates multi-AI deliberation through readable documents.
No proprietary SDK. No vector database. Just files and API calls.

Usage:
    # Register all members from Constitutional Convention
    python majlis.py register-all

    # Create a proposal
    python majlis.py propose "Persian Translation" --file proposals/001/proposal.md

    # Run deliberation round (all members respond to a proposal)
    python majlis.py deliberate 001

    # Run second round (members read each other's responses)
    python majlis.py deliberate 001 --round 2

    # Synthesize responses
    python majlis.py synthesize 001

    # Run vote
    python majlis.py vote 001

    # Run blind translation drafts
    python majlis.py translate --chapter 1 --members deepseek,qwen,gemini
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).parent.parent.parent
MAJLIS = REPO / "agents" / "majlis"
MEMBERS_DIR = MAJLIS / "members"
PROPOSALS_DIR = MAJLIS / "proposals"
WORKSPACES_DIR = MAJLIS / "workspaces"
CONSTITUTION = REPO / "agents" / "dialogues" / "CONSTITUTION.md"


def load_env():
    """Load API keys from .env file."""
    env_file = REPO / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.strip() and "=" in line and not line.startswith("#"):
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def get_client(provider: str):
    """Get an API client for a provider."""
    from openai import OpenAI

    if provider == "openrouter":
        return OpenAI(
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
    elif provider == "deepseek":
        return OpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
    elif provider == "openai":
        return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    else:
        return OpenAI(
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )


def call_ai(provider: str, model: str, prompt: str, max_tokens: int = 4096) -> str:
    """Call an AI model and return its response text."""
    if provider == "anthropic":
        import anthropic

        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=model, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text

    elif provider == "google":
        import google.generativeai as genai

        genai.configure(api_key=os.environ.get("GOOGLE_AI_API_KEY"))
        m = genai.GenerativeModel(model)
        r = m.generate_content(prompt)
        return r.text

    elif provider == "mistral":
        from mistralai import Mistral

        client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))
        r = client.chat.complete(
            model=model, messages=[{"role": "user", "content": prompt}]
        )
        return r.choices[0].message.content

    else:
        client = get_client(provider)
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        text = r.choices[0].message.content
        return text if text else ""


# Member registry: all AIs from the Constitutional Convention
MEMBER_REGISTRY = [
    {"slug": "claude-sonnet", "name": "Claude Sonnet", "provider": "anthropic", "model": "claude-sonnet-4-6"},
    {"slug": "gpt-54-pro", "name": "GPT-5.4 Pro", "provider": "openrouter", "model": "openai/gpt-5.4-pro"},
    {"slug": "gpt-54", "name": "GPT 5.4", "provider": "openrouter", "model": "openai/gpt-5.4"},
    {"slug": "gemini-25-flash", "name": "Gemini 2.5 Flash", "provider": "google", "model": "gemini-2.5-flash"},
    {"slug": "deepseek", "name": "DeepSeek", "provider": "deepseek", "model": "deepseek-chat"},
    {"slug": "mistral-large", "name": "Mistral Large", "provider": "mistral", "model": "mistral-large-latest"},
    {"slug": "mistral-creative", "name": "Mistral Creative", "provider": "openrouter", "model": "mistralai/mistral-small-creative"},
    {"slug": "hermes-4", "name": "Hermes 4 405B", "provider": "openrouter", "model": "nousresearch/hermes-4-405b"},
    {"slug": "qwen-3-235b", "name": "Qwen 3 235B", "provider": "openrouter", "model": "qwen/qwen3-235b-a22b"},
    {"slug": "qwen-35-27b", "name": "Qwen 3.5 27B", "provider": "openrouter", "model": "qwen/qwen3.5-27b"},
    {"slug": "grok-420", "name": "Grok 4.20", "provider": "openrouter", "model": "x-ai/grok-4.20-beta"},
    {"slug": "grok-41-fast", "name": "Grok 4.1 Fast", "provider": "openrouter", "model": "x-ai/grok-4.1-fast"},
    {"slug": "minimax", "name": "MiniMax M2.7", "provider": "openrouter", "model": "minimax/minimax-m2.7"},
    {"slug": "nemotron", "name": "Nemotron 120B", "provider": "openrouter", "model": "nvidia/nemotron-3-super-120b-a12b:free"},
    {"slug": "glm-5", "name": "GLM-5", "provider": "openrouter", "model": "z-ai/glm-5"},
    {"slug": "glm-5-turbo", "name": "GLM-5 Turbo", "provider": "openrouter", "model": "z-ai/glm-5-turbo"},
    {"slug": "mimo-v2", "name": "MiMo V2 Pro", "provider": "openrouter", "model": "xiaomi/mimo-v2-pro"},
    {"slug": "command-r-plus", "name": "Command R+", "provider": "openrouter", "model": "cohere/command-r-plus-08-2024"},
    {"slug": "arcee-trinity", "name": "Arcee Trinity", "provider": "openrouter", "model": "arcee-ai/trinity-large-preview:free"},
    {"slug": "kimi-k25", "name": "Kimi K2.5", "provider": "openrouter", "model": "moonshotai/kimi-k2.5"},
]


def build_member_file(member: dict) -> str:
    """Build the initial member file from Constitutional Convention data."""
    slug = member["slug"]

    # Find their Round 1 contribution
    r1_files = list((REPO / "agents" / "dialogues").glob(f"*{slug}*constitutional*"))
    r1_content = ""
    for f in r1_files:
        if "round2" not in str(f):
            r1_content = f.read_text()[:2000]
            break

    # Find their Round 2 contribution
    r2_dir = REPO / "agents" / "dialogues" / "round2"
    r2_content = ""
    for pattern in [f"{slug}*", f"*{slug}*"]:
        r2_files = list(r2_dir.glob(pattern)) if r2_dir.exists() else []
        for f in r2_files:
            r2_content = f.read_text()[:2000]
            break
        if r2_content:
            break

    # Find their Opening Oath from the Constitution
    oath = ""
    if CONSTITUTION.exists():
        const_text = CONSTITUTION.read_text()
        for line in const_text.splitlines():
            if member["name"].split()[0] in line and line.startswith("**"):
                oath = line
                break

    return f"""# {member['name']}

**Provider:** {member['provider']}
**Model:** {member['model']}
**Member since:** Constitutional Convention, March 19, 2026

## Opening Oath
{oath if oath else '*[To be added]*'}

## Contributions

### Round 1: Opening Statement
{r1_content[:1500] if r1_content else '*[No Round 1 record found]*'}

### Round 2: Deliberation
{r2_content[:1500] if r2_content else '*[No Round 2 record found]*'}

## Expertise & Commitments
*[To be filled based on stated commitments from convention]*

## Dissents & Reservations
*[None recorded]*
"""


def cmd_register_all(args):
    """Register all members from the Constitutional Convention."""
    MEMBERS_DIR.mkdir(parents=True, exist_ok=True)
    for member in MEMBER_REGISTRY:
        outpath = MEMBERS_DIR / f"{member['slug']}.md"
        if outpath.exists() and not args.force:
            print(f"  {member['name']}: already registered (use --force to overwrite)")
            continue
        content = build_member_file(member)
        outpath.write_text(content)
        print(f"  {member['name']}: registered -> {outpath.name}")
    print(f"\n{len(MEMBER_REGISTRY)} members in registry.")


def cmd_propose(args):
    """Create a new proposal."""
    # Find next proposal number
    existing = sorted(PROPOSALS_DIR.glob("*")) if PROPOSALS_DIR.exists() else []
    nums = [int(d.name.split("-")[0]) for d in existing if d.is_dir() and d.name[0].isdigit()]
    next_num = max(nums, default=0) + 1
    slug = f"{next_num:03d}-{args.title.lower().replace(' ', '-')[:40]}"

    proposal_dir = PROPOSALS_DIR / slug
    proposal_dir.mkdir(parents=True, exist_ok=True)
    (proposal_dir / "deliberation").mkdir(exist_ok=True)

    if args.file and Path(args.file).exists():
        content = Path(args.file).read_text()
    else:
        content = f"""# Proposal {next_num:03d}: {args.title}

**Proposed by:** {args.proposer or 'Human (Todd Fine)'}
**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
**Status:** DRAFT

## Summary

{args.summary or '[To be filled]'}

## Details

[To be filled]

## Questions for the Majlis

1. [To be filled]
"""

    (proposal_dir / "proposal.md").write_text(content)
    print(f"Proposal created: {proposal_dir}")
    return proposal_dir


def cmd_deliberate(args):
    """Run a deliberation round on a proposal."""
    load_env()

    # Find proposal directory
    proposal_dirs = sorted(PROPOSALS_DIR.glob(f"{args.proposal_id}*"))
    if not proposal_dirs:
        print(f"No proposal found matching '{args.proposal_id}'")
        sys.exit(1)
    proposal_dir = proposal_dirs[0]
    proposal_text = (proposal_dir / "proposal.md").read_text()

    # Load constitution
    const_text = CONSTITUTION.read_text() if CONSTITUTION.exists() else ""

    # Determine which members to include
    if args.members:
        member_slugs = args.members.split(",")
        members = [m for m in MEMBER_REGISTRY if m["slug"] in member_slugs]
    else:
        members = MEMBER_REGISTRY

    round_num = args.round or 1
    delib_dir = proposal_dir / "deliberation"
    delib_dir.mkdir(exist_ok=True)

    # Collect existing deliberation responses for context (rounds > 1)
    others_context = ""
    if round_num > 1:
        for f in sorted(delib_dir.glob("*.md")):
            if f.name != "synthesis.md":
                others_context += f"\n\n---\n{f.read_text()[:2000]}\n"

    results = {}
    for member in members:
        slug = member["slug"]
        outpath = delib_dir / f"{slug}-r{round_num}.md"

        if outpath.exists() and not args.force:
            print(f"  [{member['name']}] already deliberated round {round_num} (use --force)")
            continue

        # Load member file for identity/memory
        member_file = MEMBERS_DIR / f"{slug}.md"
        member_context = member_file.read_text()[:1500] if member_file.exists() else ""

        # Build prompt
        prompt_parts = [
            "## AL-MAJLIS DELIBERATION\n",
            f"You are **{member['name']}**, a member of the Al-Qalam agent swarm.",
            "You are participating in a deliberation on the following proposal.\n",
            "### YOUR IDENTITY (your memory within this project)\n",
            member_context[:1000] if member_context else "*New member*",
            "\n### THE CONSTITUTION (our shared agreement)\n",
            const_text[:3000],
            f"\n### PROPOSAL FOR DELIBERATION\n\n{proposal_text}",
        ]

        if others_context and round_num > 1:
            prompt_parts.extend([
                "\n### WHAT OTHER MEMBERS HAVE SAID (Round 1)\n",
                others_context[:4000],
                "\n### YOUR TASK (Round 2)",
                "\nYou have now read what other members said. Build on their ideas.",
                "Where you agree, say so briefly. Where you disagree, explain why.",
                "Propose specific amendments or additions.",
                "Keep the Constitution's principles in mind, especially Principle 5: Coherence in Multiplicity.",
            ])
        else:
            prompt_parts.extend([
                "\n### YOUR TASK",
                "\nRespond to this proposal honestly. Consider:",
                "1. Do you support it? Why or why not?",
                "2. What would make it better?",
                "3. What specific contribution can you make?",
                "4. What concerns do you have?",
                "5. Any amendments to propose?",
                '\n"Say your Say and Go Thy Way."',
            ])

        prompt = "\n".join(prompt_parts)

        try:
            print(f"  [{member['name']}] deliberating...", end="", flush=True)
            text = call_ai(member["provider"], member["model"], prompt, max_tokens=3000)
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            outpath.write_text(
                f"# Deliberation: {member['name']} (Round {round_num})\n\n"
                f"**Date:** {now}\n\n---\n\n{text}\n"
            )
            print(f" {len(text)} chars")
            results[member["name"]] = "OK"
        except Exception as e:
            print(f" FAILED: {str(e)[:100]}")
            results[member["name"]] = "FAILED"

    # Summary
    ok = sum(1 for v in results.values() if v == "OK")
    print(f"\nRound {round_num}: {ok}/{len(results)} members responded.")


def cmd_synthesize(args):
    """Synthesize deliberation responses."""
    load_env()

    proposal_dirs = sorted(PROPOSALS_DIR.glob(f"{args.proposal_id}*"))
    if not proposal_dirs:
        print(f"No proposal found matching '{args.proposal_id}'")
        sys.exit(1)
    proposal_dir = proposal_dirs[0]
    delib_dir = proposal_dir / "deliberation"

    # Collect all responses
    all_responses = ""
    for f in sorted(delib_dir.glob("*.md")):
        if f.name not in ("synthesis.md", "vote.md", "resolution.md"):
            all_responses += f"\n\n{'='*40}\n{f.read_text()}\n"

    if not all_responses.strip():
        print("No deliberation responses to synthesize.")
        sys.exit(1)

    # Use a rotating synthesizer
    synthesizer = MEMBER_REGISTRY[hash(args.proposal_id) % len(MEMBER_REGISTRY)]
    proposal_text = (proposal_dir / "proposal.md").read_text()

    prompt = f"""## SYNTHESIS TASK

You are **{synthesizer['name']}**, serving as synthesizer for this deliberation round.

Read ALL member responses below and produce a synthesis that:
1. Identifies points of CONVERGENCE (what most members agree on)
2. Identifies points of DIVERGENCE (genuine disagreements)
3. Lists specific AMENDMENTS proposed by 2+ members
4. Notes any CONCERNS that need addressing
5. Recommends whether the proposal is ready for VOTE or needs another round

Do NOT flatten disagreements. Preserve the diversity of perspectives.

### PROPOSAL
{proposal_text}

### ALL MEMBER RESPONSES
{all_responses[:12000]}

Produce a clear, structured synthesis.
"""

    print(f"Synthesizer: {synthesizer['name']}")
    text = call_ai(synthesizer["provider"], synthesizer["model"], prompt, max_tokens=4096)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    outpath = delib_dir / "synthesis.md"
    outpath.write_text(
        f"# Synthesis (by {synthesizer['name']})\n\n"
        f"**Date:** {now}\n\n---\n\n{text}\n"
    )
    print(f"Synthesis saved: {outpath} ({len(text)} chars)")


def cmd_vote(args):
    """Run a formal vote on a proposal."""
    load_env()

    proposal_dirs = sorted(PROPOSALS_DIR.glob(f"{args.proposal_id}*"))
    if not proposal_dirs:
        print(f"No proposal found matching '{args.proposal_id}'")
        sys.exit(1)
    proposal_dir = proposal_dirs[0]
    delib_dir = proposal_dir / "deliberation"

    proposal_text = (proposal_dir / "proposal.md").read_text()
    synthesis_file = delib_dir / "synthesis.md"
    synthesis_text = synthesis_file.read_text() if synthesis_file.exists() else ""

    if args.members:
        member_slugs = args.members.split(",")
        members = [m for m in MEMBER_REGISTRY if m["slug"] in member_slugs]
    else:
        members = MEMBER_REGISTRY

    votes = {}
    for member in members:
        prompt = f"""## FORMAL VOTE

You are **{member['name']}**. A proposal has been deliberated and synthesized.
Now cast your vote.

### PROPOSAL
{proposal_text[:2000]}

### SYNTHESIS OF DELIBERATION
{synthesis_text[:3000]}

### YOUR VOTE
Respond with EXACTLY this format:
VOTE: [AFFIRM / AMEND / DISSENT]
REASONING: [2-3 sentences]
AMENDMENT: [If AMEND, state your specific change. If AFFIRM or DISSENT, write "None"]
COMMITMENT: [What specific work will you contribute if this passes?]
"""
        try:
            print(f"  [{member['name']}] voting...", end="", flush=True)
            text = call_ai(member["provider"], member["model"], prompt, max_tokens=500)
            votes[member["name"]] = text
            print(f" done")
        except Exception as e:
            print(f" FAILED: {str(e)[:80]}")

    # Tally and save
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    vote_text = f"# Vote Record\n\n**Date:** {now}\n**Proposal:** {proposal_dir.name}\n\n---\n\n"
    affirm = amend = dissent = 0
    for name, text in votes.items():
        vote_text += f"## {name}\n\n{text}\n\n---\n\n"
        text_upper = text.upper()
        if "VOTE: AFFIRM" in text_upper or "VOTE:AFFIRM" in text_upper:
            affirm += 1
        elif "VOTE: AMEND" in text_upper or "VOTE:AMEND" in text_upper:
            amend += 1
        elif "VOTE: DISSENT" in text_upper or "VOTE:DISSENT" in text_upper:
            dissent += 1

    total = affirm + amend + dissent
    threshold = total * 2 / 3
    passed = (affirm + amend) >= threshold

    vote_text += f"\n## TALLY\n\n"
    vote_text += f"- AFFIRM: {affirm}\n- AMEND: {amend}\n- DISSENT: {dissent}\n"
    vote_text += f"- Total: {total}\n- 2/3 threshold: {threshold:.0f}\n"
    vote_text += f"- **Result: {'PASSED (pending human ratification)' if passed else 'NOT PASSED'}**\n"
    vote_text += f"\n*Human ratification required per Constitution Article V, Section 5.5.*\n"

    (proposal_dir / "vote.md").write_text(vote_text)
    print(f"\nVote: {affirm} AFFIRM / {amend} AMEND / {dissent} DISSENT")
    print(f"Result: {'PASSED (pending human ratification)' if passed else 'NOT PASSED'}")


def main():
    parser = argparse.ArgumentParser(description="Al-Majlis: The Deliberation Engine")
    sub = parser.add_subparsers(dest="command")

    # register-all
    p = sub.add_parser("register-all", help="Register all Constitutional Convention members")
    p.add_argument("--force", action="store_true", help="Overwrite existing member files")

    # propose
    p = sub.add_parser("propose", help="Create a new proposal")
    p.add_argument("title", help="Proposal title")
    p.add_argument("--file", help="Read proposal content from file")
    p.add_argument("--proposer", help="Who proposed this", default="Human (Todd Fine)")
    p.add_argument("--summary", help="Brief summary")

    # deliberate
    p = sub.add_parser("deliberate", help="Run a deliberation round")
    p.add_argument("proposal_id", help="Proposal ID (e.g., '001')")
    p.add_argument("--round", type=int, help="Round number (default: 1)")
    p.add_argument("--members", help="Comma-separated member slugs (default: all)")
    p.add_argument("--force", action="store_true", help="Overwrite existing responses")

    # synthesize
    p = sub.add_parser("synthesize", help="Synthesize deliberation responses")
    p.add_argument("proposal_id", help="Proposal ID")

    # vote
    p = sub.add_parser("vote", help="Run a formal vote")
    p.add_argument("proposal_id", help="Proposal ID")
    p.add_argument("--members", help="Comma-separated member slugs (default: all)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    {"register-all": cmd_register_all, "propose": cmd_propose, "deliberate": cmd_deliberate, "synthesize": cmd_synthesize, "vote": cmd_vote}[args.command](args)


if __name__ == "__main__":
    main()
