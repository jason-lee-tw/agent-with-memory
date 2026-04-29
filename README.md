# Agent Memory

## Project Description

This is a simple example of building memory management system for AI Agent (Claude in this example).

## Pre-requisite

- `Python:3.14` is installed.
- `UV` is installed.

## Run program

```sh
# Initialize program environment
uv sync

# Run program
uv run ./src/main.py
```

## Project structure

```
agent-memory/
├── src/
│   ├── main.py                        # Entry point: initialises the agent, seeds knowledge, and runs the REPL loop
│   ├── agents/
│   │   ├── claude_agent.py            # ClaudeAgent – wraps the LLM and exposes learn_fact, learn_procedure, and query
│   │   └── agent_memory.py            # AgentMemory – manages semantic (facts), episodic (conversations), procedural, and working memory
│   └── constants/
│       └── memory_constants.py        # Shared constants (e.g. MEMORY_PATH for the on-disk memory directory)
├── temp/
│   └── agent-memory/                  # Runtime JSON files written by AgentMemory (git-ignored)
│       ├── facts_semantic.json        # Persisted facts (semantic memory)
│       ├── converstation_epicsodic.json  # Persisted conversation history (episodic memory)
│       └── procedures.json            # Persisted step-by-step procedures (procedural memory)
├── .env.template                      # Template for required environment variables (copy to .env)
├── pyproject.toml                     # Project metadata and dependencies (managed by uv)
└── uv.lock                            # Locked dependency versions
```

**Where to look for what:**

| Concern                                        | Location                            |
| ---------------------------------------------- | ----------------------------------- |
| Starting the program / conversation loop       | `src/main.py`                       |
| LLM integration and prompt construction        | `src/agents/claude_agent.py`        |
| Memory storage, search, and context generation | `src/agents/agent_memory.py`        |
| File paths and shared configuration values     | `src/constants/memory_constants.py` |
| Persisted memory data (created at runtime)     | `temp/agent-memory/*.json`          |
