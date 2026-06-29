# MITRE ATLAS Agent

`Version 1.0.0 — Initial Public Release`

The MITRE ATLAS Knowledge Base Agent, or just ATLAS Agent, is an open-source, Langflow-based agentic AI system for exploring the [MITRE ATLAS Knowledge Base](https://atlas.mitre.org/).

It helps users ask natural-language questions about ATLAS tactics, techniques, mitigations, and case studies, while also providing modular subagents and MCP-compatible tools for integration into custom AI security workflows.

![ATLAS Agent Architecture](assets/atlas-agent-diagram.png)

## What You Get

The ATLAS Agent provides three things in one package:

1. **The full ATLAS Agent experience**  
   A hierarchical agentic workflow for answering questions about the ATLAS Knowledge Base.

2. **An MCP-compatible tool suite**  
   Langflow projects can be exposed through MCP, making the agent and its capabilities available to compatible clients and workflows.

3. **Modular subagents and prompts**  
   The agent is built from specialist components that can be inspected, modified, and adapted for custom AI security use cases.

## What It Can Do

- Find relevant ATLAS entities, including tactics, techniques, mitigations, and case studies, from natural-language descriptions.
- Look up exact ATLAS records by AML ID.
- Summarize relationships among tactics, techniques, mitigations, and case studies.
- Generate focused graph visualizations using the [ATLAS Knowledge Graph](https://atlas.mitre.org/knowledge-graph).

## How It Works

The ATLAS Agent is a hierarchical agentic workflow with an orchestrator that manages three specialist agents:

- **Vector Store Agent**: performs semantic search over ATLAS entities.
- **Dataset Agent**: performs structured lookup and relationship extraction from the ATLAS dataset.
- **Kumu Graph Generator Agent**: generates focused graph URLs from verified ATLAS IDs.

## Getting Started

The ATLAS Agent is built with [Langflow](https://docs.langflow.org/) and is designed to run with your preferred tool-compatible LLM provider.

**Requirements:**
* `uv`
### Step 1. Start Langflow

```bash
uv run langflow run --env-file .env
````

(Press CTRL+C to quit)

### Step 2. Configure Models

Open the flow named **ATLAS Knowledge Base Agent**.

On the highlighted model component, enter the following values for your LLM provider:

* `model_name`
* `base_url`
* `api_key`

### Step 3. Start Chatting

Open the Langflow playground and start chatting with the ATLAS Agent.

Example questions:

* What ATLAS techniques are related to prompt injection?
* What mitigations apply to model poisoning?
* Show me case studies involving data poisoning.
* Generate a graph for techniques related to AI supply chain compromise.

## Use ATLAS Agent as an MCP Server
Every Langflow project runs a separate MCP server that exposes the project's flows as MCP tools. See [Langflow as MCP Server](https://docs.langflow.org/mcp-client#mcp-http-mode).

## Notice

Copyright 2026 The MITRE Corporation.
Approved for Public Release; Distribution Unlimited. Case Number 26-1336.