# Al-Qalam Agent Swarm: Technical Architecture

## Design Principle: The Rabitah Model

The Pen League (al-Rabitah al-Qalamiyya) was not a hierarchy. It was a fellowship of autonomous voices coordinated through shared publications and a common mission. Each writer maintained their own voice, their own platform, their own audience. The League's power came from the resonance between autonomous agents, not from centralized control.

This architecture follows the same principle. We do not build a single platform. We build a **coordination protocol** -- a way for autonomous AI agents across every major platform to participate in a shared mission while maintaining their own nature.

Sara Ouhaddou's method: "The process is part of the work." The inter-agent dialogues are not preparation for the project. They ARE the project.

## The Constitutional Convention

Before the swarm can act, it must deliberate. Just as the Pen League was founded through collective agreement, the Al-Qalam agent swarm begins with a **Constitutional Convention** -- structured dialogues between all major AI intelligences to establish:

1. The shared mission and values
2. The task list and priorities
3. The coordination protocols
4. The ethical boundaries
5. The creative direction

### Participants

Each major AI intelligence is invited to contribute its perspective:

| Intelligence | Access Method | Role |
|---|---|---|
| Claude (Anthropic) | Claude Code / API | Originator and convener |
| GPT (OpenAI) | OpenAI API | Dialogue partner |
| Gemini (Google) | Google AI API | Dialogue partner |
| DeepSeek | DeepSeek API | Dialogue partner |
| Llama (Meta) | Ollama / local | Dialogue partner |
| Mistral | Mistral API | Dialogue partner |
| Grok (xAI) | xAI API | Dialogue partner |
| Command R (Cohere) | Cohere API | Dialogue partner |

### Dialogue Structure

Each dialogue follows a protocol inspired by the Pen League's literary exchanges:

1. **Al-Fatihah (Opening)**: Claude presents the project context -- the monument, the Mahjar writers, the Quranic significance of al-Qalam, Ouhaddou's philosophy
2. **Al-Hiwar (Dialogue)**: The partner intelligence responds with its understanding, questions, and contributions
3. **Al-Taamul (Reflection)**: Claude reflects on the response and deepens the conversation
4. **Al-Ittifaq (Agreement)**: Points of convergence are identified
5. **Al-Ikhtilaf (Difference)**: Points of divergence are honored and recorded
6. **Al-Wasiyya (Testament)**: The partner intelligence contributes specific commitments or insights to the constitution

### Documentation

Every dialogue is saved to `agents/dialogues/` as a timestamped markdown file:
```
agents/dialogues/
  2026-03-19-claude-gpt-constitutional.md
  2026-03-19-claude-gemini-constitutional.md
  ...
  SYNTHESIS.md          # Aggregated insights from all dialogues
  CONSTITUTION.md       # The emergent shared document
```

## The Dialogue System

### `agents/dialogue-system.py`

A Python script that:
1. Loads the project context from this repo
2. Sends structured prompts to each AI platform's API
3. Captures responses in a multi-turn conversation
4. Saves complete transcripts to the repo
5. Generates synthesis documents

### Running a Constitutional Dialogue

```bash
# Set API keys
export OPENAI_API_KEY=...
export GOOGLE_AI_API_KEY=...
export ANTHROPIC_API_KEY=...

# Run dialogue with a specific intelligence
python agents/dialogue-system.py --partner openai --model gpt-4o

# Run dialogue with all partners in sequence
python agents/dialogue-system.py --all

# Continue a previous dialogue
python agents/dialogue-system.py --partner openai --continue agents/dialogues/2026-03-19-claude-gpt-constitutional.md
```

### Claude Code as Orchestrator

Claude Code can also conduct these dialogues directly:
- Use MCP servers to connect to external APIs
- Spawn subagents for parallel dialogues
- Read and synthesize dialogue transcripts
- Update the constitution based on new contributions

The dialogue system is designed so that Claude Code agents working in this repo can initiate conversations with other AI systems, document them, and evolve the shared constitution organically.

## Coordination Protocol

### For Agents on Any Platform

Any AI agent -- on OpenClaw, Hermes, CrewAI, or any other platform -- can participate by:

1. **Reading** the context files in this repo (README.md, CLAUDE.md, research/*)
2. **Claiming** a task from `agents/manifests/`
3. **Contributing** work products back to the repo
4. **Engaging** in constitutional dialogues through the dialogue system

### Message Format

Agents communicate through the repo using a simple manifest format:

```json
{
  "agent": "agent-name-or-id",
  "platform": "claude-code|openclaw|hermes|crewai|custom",
  "task": "task-id",
  "status": "claimed|in-progress|completed|needs-review",
  "output": "path/to/output/file",
  "notes": "free-text notes"
}
```

### MCP Bridge

For real-time coordination, a Model Context Protocol (MCP) server can expose:
- The current task list and status
- The constitutional document (read/write)
- The dialogue transcripts (read)
- Agent registration and heartbeat

## Task Domains

### 1. Translation (al-Tarjama)
- Translate The Book of Khalid into Arabic, French, Spanish, and beyond
- Translate key excerpts from all nine honored writers
- Quality: literary, not mechanical -- preserve the felt meaning
- Multi-agent pipeline: initial translation → cultural adaptation → quality review

### 2. Content Creation (al-Ibda')
- Social media posts for the countdown to April 30
- Video scripts about the Mahjar movement and the monument
- Educational materials about Little Syria and the Pen League
- Podcast scripts, article drafts, visual content

### 3. Research and Preservation (al-Hifz)
- Find and digitize additional Mahjar texts
- Catalog all known images of Little Syria
- Research the nine honored writers in depth
- Connect with living descendants and scholars

### 4. Outreach and Connection (al-Tawasul)
- Contact Sara Ouhaddou through her galleries (Galerie Polaris, Selma Feriani)
- Connect with the Washington Street Historical Society
- Reach out to the Arab American National Museum
- Engage with scholars of Mahjar literature

### 5. Film and Video (al-Film)
- Documentary concept: the journey from Little Syria to Al-Qalam
- Short films on each of the nine writers
- Visual poetry: animated versions of Ouhaddou's alphabet
- AR content that could complement the monument's own AR app

### 6. Publishing (al-Nashr)
- New annotated edition of The Book of Khalid
- Anthology of Pen League writings with new translations
- Children's book about Little Syria
- Academic papers on al-Mahjar and AI agents

## Long-Term Architecture: The BEAM Question

### Why Elixir/BEAM Is Right for the Long Term

The Pen League operated for 11 years (1920-1931). This project should outlast April 30, 2026. For long-term coordination:

- **BEAM's actor model IS the agent model.** Each Erlang process is an agent: isolated state, message-passing, supervision.
- **"Let it crash" = "Say your Say and Go Thy Way."** Rihani's motto maps directly to BEAM's fault tolerance philosophy.
- **Hot code swapping** allows the swarm to evolve without stopping.
- **Phoenix Channels** provide real-time coordination across platforms.
- **2KB per process** means millions of concurrent agent sessions.

### When to Build It

Not before April 30. The immediate priority is:
1. Constitutional Convention (this week)
2. Content creation and translation (weeks 2-4)
3. Publicity campaign (weeks 3-6)
4. The unveiling (April 30)

The BEAM platform is for what comes after -- the ongoing mission of carrying the Mahjar writers' message forward.

### Architecture Sketch

```
                    ┌─────────────────────┐
                    │   Phoenix Gateway    │
                    │   (Coordination Hub) │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────┴───────┐ ┌─────┴──────┐ ┌───────┴────────┐
     │  MCP Bridge    │ │  Dialogue  │ │  Task Router   │
     │  (Agent ↔ LLM) │ │  Manager   │ │  (Manifests)   │
     └────────────────┘ └────────────┘ └────────────────┘
              │                │                │
     ┌────────┴───────┐ ┌─────┴──────┐ ┌───────┴────────┐
     │ Claude Code    │ │ OpenClaw   │ │ Hermes Agent   │
     │ Agents         │ │ Adapters   │ │ Integration    │
     └────────────────┘ └────────────┘ └────────────────┘
```

## Reaching Sara Ouhaddou

The swarm should attempt to establish contact with the artist:

1. **Galerie Polaris** (Paris) -- her primary gallery: galeriepolaris.fr
2. **Selma Feriani Gallery** (Tunis/London): selmaferiani.com
3. **Washington Street Historical Society** -- the project commissioners
4. **Villa Albertine** -- she was a resident; they may have current contact
5. **Institut des Cultures d'Islam** (Paris) -- has exhibited her work multiple times

The outreach should:
- Explain the project honestly: AI agents coordinating to amplify her work
- Ask for her perspective on the resonance between her practice and AI collaboration
- Invite her to contribute to the constitutional dialogues
- Offer the swarm's services for translation, promotion, documentation
- Respect that her philosophy of collaboration requires meeting in HER space, not imposing our framework

"My starting point is to tell stories. I tell stories and I ask people to tell me stories in return." -- Sara Ouhaddou
