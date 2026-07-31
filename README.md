# MITRE ATLAS Agent

`Version 1.1.0 — Single-Agent Release · ATLAS data v2026.7`

The ATLAS Agent is an open-source AI assistant for exploring the MITRE ATLAS Knowledge Base.

It gives you three ways to work with ATLAS:

1. **A natural-language guide for any user**  
    Learn about ATLAS tactics, techniques, mitigations, and case studies by asking questions in plain English.
2. **MCP server and API access**  
    Use the agent and its capabilities inside compatible tools, workflows, and custom applications.
3. **Fully open-source and customizable**  
    Inspect, modify, and tailor prompts, behavior, and tools to fit specific security workflows and research needs.

**Ask questions. Explore relationships. Generate knowledge graphs. Integrate ATLAS into your workflow.**

## How It Works

The ATLAS Agent uses a single agent with direct access to three purpose-built tools. This streamlined architecture reduces handoffs and complexity for faster responses while retaining the core ATLAS research capabilities:

- **Vector Store**: performs semantic search over ATLAS entities.
- **Dataset**: performs structured lookup and relationship extraction from the ATLAS dataset.
- **Graph Visualizer**: generates focused graph URLs from verified ATLAS IDs.

![ATLAS Agent Architecture](assets/atlas-agent-diagram.png)

The bundled dataset and vector store are synchronized with the MITRE ATLAS data release `v2026.7`.

## Getting Started

The ATLAS Agent is built with [Langflow](https://docs.langflow.org/) and is designed to run with your preferred tool-compatible LLM provider.

**Requirements:**
* `uv`

### Step 1. Start Langflow

Navigate to `atlas-agent/` and run the following command.

```bash
uv run langflow run --env-file .env
```

(Press CTRL+C to quit)

### Step 2. Configure Models

Open the flow named **ATLAS Agent v1.1.0**.

On the highlighted model component, enter the following values for your LLM provider:

* `Model Name`
* `API Base URL`
* `API Key`

Langflow offers several LLM components.

### Step 3. Start Chatting

Open the Langflow playground and start chatting with the ATLAS Agent.

Example questions:

* What ATLAS techniques are related to prompt injection?
* What mitigations apply to model poisoning?
* Show me case studies involving data poisoning.
* Generate a graph for techniques related to AI supply chain compromise.

## Access the ATLAS Agent as an MCP Server

Every Langflow project runs a separate MCP server that exposes the project's flows as MCP tools. See [Langflow as MCP Server](https://docs.langflow.org/mcp-client#mcp-http-mode).

## Release Notes

See [CHANGELOG.md](CHANGELOG.md) for release history and upgrade notes.

## Notice

Copyright 2026 The MITRE Corporation.
Approved for Public Release; Distribution Unlimited. Case Number 26-1336.
