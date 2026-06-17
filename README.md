# MITRE ATLAS Knowledge Base Agent

`Version 1.0.0 Initial Public Release`

The ATLAS Knowledge Base (KB) Agent is a Langflow-based agentic AI system that helps answer questions about the [MITRE ATLAS Knowledge Base](https://atlas.mitre.org/).

![alt text](assets/atlas-agent-architecture.png)

## What It Can Do

- Find relevant ATLAS entities (tactics, techniques, mitigations, and case studies) from natural-language descriptions.
- Look up exact ATLAS records by AML ID.
- Summarize relationships among tactics, techniques, mitigations, and case studies.
- Generate focused graph visualizations using the [ATLAS Knowledge Graph](https://atlas.mitre.org/knowledge-graph).

## How It Works

The ATLAS KB Agent is a hierarchical agentic workflow with an ochestrator which manages three specialist agents:

- **Vector Store Agent**: semantic search over ATLAS entities.
- **Dataset Agent**: structured lookup and relationship extraction from the ATLAS dataset.
- **Kumu Graph Generator Agent**: focused graph URL generation from verified ATLAS IDs.

## Getting Started

The ATLAS KB Agent is an open-sourced application built using [Langflow](https://docs.langflow.org/). 

#### 1. Start Langflow

```
uv run langflow run --env-file .env
```

#### 2. Configure Models
Open the flow called, "ATLAS Knowledge Base Agent" and on the highlighted component, enter the `model_name`, `base_url`, and `api_key` for your tool-compatible LLM provider of choice.

#### 3. Start Chatting
Open up the playground to start chatting with the ATLAS KB Agent.

## Notice

Copyright 2026 The MITRE Corporation. 
Approved for Public Release; Distribution Unlimited. Case Number 26-1336.