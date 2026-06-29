# MITRE ATLAS Agent

`Version 1.0.0 — Initial Public Release`

The ATLAS Knowledge Base Agent is an open-source AI assistant for exploring the MITRE ATLAS Knowledge Base.

It gives you three ways to work with ATLAS:

1. **A natural-language guide for any user**  
    Learn about ATLAS tactics, techniques, mitigations, and case studies by asking questions in plain English.
2. **MCP server and API access**  
    Use the agent and its capabilities inside compatible tools, workflows, and custom applications.
3. **Fully open-source and customizable**  
    Inspect, modify, and tailor prompts, behavior, and subagents to fit specific security workflows and research needs.

**Ask questions. Explore relationships. Generate knowledge graphs. Integrate ATLAS into your workflow.**

![ATLAS Agent Clip](assets/atlas-agent-clip.gif)

## How It Works

The ATLAS Agent is a hierarchical agentic workflow with an orchestrator that manages three specialist agents:

- **Vector Store Agent**: performs semantic search over ATLAS entities.
- **Dataset Agent**: performs structured lookup and relationship extraction from the ATLAS dataset.
- **Kumu Graph Generator Agent**: generates focused graph URLs from verified ATLAS IDs.

![ATLAS Agent Architecture](assets/atlas-agent-diagram.png)

## Getting Started

The ATLAS Agent is built with [Langflow](https://docs.langflow.org/) and is designed to run with your preferred tool-compatible LLM provider.

**Requirements:**
* `uv`

### Step 1. Start Langflow

Navigate to `atlas-knowledge-base-agent/` and run the following command.

```bash
uv run langflow run --env-file .env
```

(Press CTRL+C to quit)

### Step 2. Configure Models

Open the flow named **ATLAS Agent**.

On the highlighted model component, enter the following values for your LLM provider:

* `Model Name`
* `API Base URL`
* `API Key`

### Step 3. Start Chatting

Open the Langflow playground and start chatting with the ATLAS Agent.

Example questions:

* What ATLAS techniques are related to prompt injection?
* What mitigations apply to model poisoning?
* Show me case studies involving data poisoning.
* Generate a graph for techniques related to AI supply chain compromise.

## Other ways to access the ATLAS Agent

1. **MCP Server:** Every Langflow project runs a separate MCP server that exposes the project's flows as MCP tools. See [Langflow as MCP Server](https://docs.langflow.org/mcp-client#mcp-http-mode).
2. API Access

## Notice

Copyright 2026 The MITRE Corporation.
Approved for Public Release; Distribution Unlimited. Case Number 26-1336.