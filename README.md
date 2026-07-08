# Multi-Agent Research System (MARS)

This repository configures a modular, hub-and-spoke multi-agent system designed to run natively inside the **Claude CLI**. By leveraging Claude's native agent routing and delegation features, the system coordinates parallel information retrieval, structured analysis, and schema-validated synthesis.

---

## 🏛️ System Architecture & Directory Design

The orchestration is implemented using Claude CLI Agent Definitions under the `.claude/` configuration directory.

```
.claude/
├── agents/
│   ├── coordinator.md   # Hub: orchestrates tasks, delegates to spokes
│   ├── search.md        # Spoke: file & web search retriever
│   ├── analysis.md      # Spoke: read-only fact classifier
│   └── synthesis.md     # Spoke: read-write JSON report compiler
└── schemas/
    ├── search.json      # JSON Schema for search subagent outputs
    ├── analysis.json    # JSON Schema for analysis subagent outputs
    └── report.json      # JSON Schema for synthesis subagent report
```

### 🧬 Isolation & Handoff Principles

1. **Zero Context Inheritance**: Subagents are executed in clean, isolated context windows. They do not share memory or general conversation history with the Coordinator. The Coordinator explicitly passes all target queries, rules, and parameters inside the subagent delegation prompt.
2. **Built-in Tool Allowlists**: To enforce security and operational boundaries, subagent access is restricted via the YAML frontmatter `tools` configuration:
   * **Coordinator**: Authorized to use the `Agent` (or `Task`) tool to spawn subagents.
   * **Search Subagent**: Scoped to file search and web search capabilities (`web-search`, `glob`, `grep`, `read`).
   * **Analysis Subagent**: Scoped to read-only capabilities (`glob`, `grep`, `read`).
   * **Synthesis Subagent**: Scoped to data editing and compilation capabilities (`read`, `write`).

---

## 🚀 Orchestration Workflow

```
                  ┌──────────────────────┐
                  │     User Prompt      │
                  └──────────┬───────────┘
                             │
                             ▼
               ┌──────────────────────────┐
               │    Coordinator Agent     │ [tools: ["Agent"]]
               └─────────────┬────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼ (Single-turn Parallel Spawn)     ▼ (Single-turn Parallel Spawn)
  ┌──────────────────┐              ┌──────────────────┐
  │  Search Subagent │              │Analysis Subagent │
  │ [tools: Search]  │              │ [tools: Read]    │
  └─────────┬────────┘              └─────────┬────────┘
            │                                 │
            └────────────────┬────────────────┘
                             │
                             ▼ (Consolidated Context with Provenance)
               ┌──────────────────────────┐
               │    Synthesis Subagent    │ [tools: ["Read", "Write"]]
               └─────────────┬────────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │ JSON Verification  │ (Validated against schemas)
                  └────────────────────┘
```

1. **Decomposition & Concurrency**: The Coordinator decomposes the query, spawning both the **Search** and **Analysis** subagents in parallel during a single turn using concurrent `Task`/`Agent` tool invocations.
2. **Schema Control**: Subagents must return structured JSON conforming to their designated schemas (e.g. `.claude/schemas/search.json`).
3. **Synthesis & Citation**: The Synthesis subagent compiles findings, classifying them into *Well-established*, *Contested*, and *Single-source* categories, keeping a strict provenance trace (`source_url`, `excerpt`, `confidence`, `timestamp`, `agent_id`).
