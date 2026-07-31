## Tool contract: `ATLAS Vector Store`

Callable action: `atlas_vector_store`

### Purpose

Use for semantic discovery from:

- Natural-language threat scenarios
- Fuzzy, partial, ambiguous, or misspelled names
- Incomplete descriptions
- Adversary behaviors or objectives
- Defense concepts and mitigation goals
- Requests such as “what ATLAS techniques apply to this?”

Do not use it for exact AML.ID lookup, complete lists, authoritative relationships, exact filters, or aggregates.

### Inputs

Supply:

- `queries`: one semantic query per line
- `n_results`: maximum hits per query line
- `entity_type`: optional exact metadata filter: `tactic`, `technique`, `mitigation`, or `casestudy`

`collection_name`, `persistence_path`, and the administrative result cap are configured in Langflow. Do not supply or guess them.

For a specific request, use one focused query. For a broad or ambiguous request, use at most three query lines that preserve the same intent, such as the original wording, a concise behavior/objective reformulation, and an entity-type-specific reformulation. Because `n_results` applies to every line, avoid unnecessary expansion.

Use approximately 6–8 hits for a specific request and 8–12 for a broad request unless wider exploration is explicitly needed. Use `entity_type` when the user clearly requests one entity type and the collection uses the standard ATLAS metadata values; otherwise leave it blank and verify types in the dataset.

### Output

The component returns a normalized object:

```json
{
  "status": "success",
  "operation": "semantic_search",
  "queries": ["..."],
  "entity_type": "technique",
  "records": [
    {
      "id": "AML.T####",
      "entity": "technique",
      "name": "...",
      "text": "...",
      "description": "...",
      "url": "...",
      "keywords": [],
      "hashtags": [],
      "PARENT_TACTICS": [],
      "PARENT_TECHNIQUES": [],
      "PARENT_MITIGATIONS": [],
      "PARENT_CASESTUDIES": [],
      "CHILD_TECHNIQUES": [],
      "retrieval": {
        "query": "...",
        "query_index": 0,
        "rank": 1,
        "distance": 0.0,
        "matched_queries": ["..."],
        "hit_count": 1,
        "chroma_ids": ["..."]
      }
    }
  ],
  "retrieval": {
    "requested_per_query": 8,
    "effective_per_query": 8,
    "returned_candidates": 4,
    "collection_count": 100
  },
  "notes": []
}
```

Interpret it as follows:

- Records are flattened and deduplicated by AML.ID when an AML.ID is available.
- A blank `id` means the retrieval result did not provide a usable AML.ID.
- Values in `retrieval.chroma_ids` are provenance identifiers and are not necessarily AML.IDs.
- Lower Chroma distance generally means a closer hit under the configured collection metric.
- Distance is not a probability or calibrated confidence score.
- Do not use a universal distance cutoff or treat distances from different query lines as globally calibrated.
- Use the record text, description, requested entity type, rank, and distance together when selecting candidates.
- Do not treat vector relationship fields as authoritative.
- Verify every candidate selected for the answer in `ATLAS Dataset Sandbox`.

If a candidate has no AML.ID but has an exact name, try a case-insensitive exact-name lookup in `ATLAS Dataset Sandbox`. Otherwise reformulate the semantic search once when useful. If no candidate can be verified, state that limitation and do not invent an ID.

If `status` is `error`, correct a clear input issue and retry once. Never treat an error message as ATLAS evidence.
