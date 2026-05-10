# ATLAS Agent MCP Server

## What the ATLAS Agent Does

The ATLAS Agent is a Langflow-based orchestration workflow for answering questions about MITRE ATLAS: the Adversarial Threat Landscape for Artificial Intelligence Systems. ATLAS organizes adversary behavior against AI-enabled systems into tactics, techniques, mitigations, and case studies, each identified with an AML ID such as `AML.T0051`, `AML.M0028`, or `AML.CS0001`.

The agent is designed as an orchestrator with specialized agents. The orchestrator interprets the user's question, decides which specialist should retrieve evidence, and synthesizes a final answer grounded in ATLAS records instead of inventing facts.

## Specialized Agents

- **Vector Store Agent**: Performs semantic search over ATLAS entities. It is best for natural-language questions, approximate entity names, threat scenarios, defense concepts, or broad discovery tasks.
- **CSV Agent**: Performs structured lookup and relationship extraction over the ATLAS CSV dataset. It is best for exact AML IDs, entity fields, parent tactics, child techniques, related mitigations, and case-study relationships.
- **Kumu Graph Generator Agent**: Builds focused Kumu subgraph URLs from verified ATLAS IDs. It is best when the user asks for a graph, map, visualization, embed, or ATLAS relationship view.

Typical routing:

1. Natural-language question: semantic search with the Vector Store Agent, then CSV verification and relationship hydration.
2. Exact AML ID question: structured lookup with the CSV Agent, with optional relationship expansion.
3. Mitigation or case-study question: identify relevant techniques, retrieve related mitigations or case studies, then summarize.
4. Graph request: verify the relevant IDs, then generate a focused Kumu subgraph.

## MCP Server

The deployed MCP server exposes the ATLAS Agent as a tool to MCP-compatible clients.

## MCP Client Setup


---

## Instructions for Connecting to MCP Server


## Instructions for AIP VM Deployment

##### 1. Setup Environment

```bash
cp .env.example .env
```

##### 2. Build Image

```bash
docker build -t langflow-mitre:latest .
```

##### 3. Check that Volume Exists

```bash
docker volume ls
```

If `langflow-data` does not exist, create it.

```bash
docker volume create langflow-data
```

##### 3. Start/Create Container

Check to see that the `langflow` container is running.

```bash
docker ps -a
```

If it's running, skip to step 4.

If it's not running, start it.

```bash
docker start langflow
```

If you don't see it, create it.


```bash
docker run -p 7860:7860 \
  --env-file .env \
  --name langflow \
  -v langflow-data:/app/.langflow \
  --restart unless-stopped \
  langflow-mitre:latest
```


##### 4. Open UI

```
http://localhost:7860
```

---

## Flow & Component Loading Behavior

By default, Langflow can sync from local folders:

* `flows/`
* `components/`

If enabled, these will **overwrite matching entries in `langflow.db` (by ID)** on startup.

**To prevent overwrites**, ensure these are commented out in `.env`:

```bash
# LANGFLOW_LOAD_FLOWS_PATH=./flows
# LANGFLOW_COMPONENTS_PATH=./components
```

**To intentionally sync from folders**, uncomment:

```bash
LANGFLOW_LOAD_FLOWS_PATH=./flows
LANGFLOW_COMPONENTS_PATH=./components
```

---

## Collaboration Model

### How it works

* Each user:

  * Pulls this repo on the VM
  * Runs their own container
* All containers share:

  * `langflow-data` volume
  * Same `langflow.db`

Result:

* Multiple containers → **one shared Langflow state**

### Recommended Workflow

* Treat Langflow **Projects** like Git branches:

  * `main` → stable
  * `dev` → integration
  * `<user>` → personal work

* Coordinate changes:

  * Avoid simultaneous edits on the same flow
  * Merge flows manually within the UI

* Backups:

  * Regularly export flows/components
  * Store in GitLab
  * Use a separate directory (e.g., `backups/`) if not syncing via `flows/`

---

## Volume Management

### Create volume (if missing)

```bash
docker volume create langflow-data
```

### Recovery from exports

1. Place exported JSON files into `flows/`
2. Enable loading in `.env`:

```bash
LANGFLOW_LOAD_FLOWS_PATH=./flows
```

3. Restart container to re-import

---

## Key Takeaways

* **Do not delete `langflow-data`** unless intentionally resetting state
* **Flows in `flows/` can overwrite DB entries**
* **All users share one database via Docker volume**
* **Coordination is required to avoid conflicts**


