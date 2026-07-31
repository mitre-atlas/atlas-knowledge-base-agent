## Tool contract: `ATLAS Graph Generator`

Callable action: `atlas_graph_generator`

### Purpose

Use only when the user explicitly requests a graph, map, Kumu URL, iframe, network, visualization, or subgraph.

It generates a URL and iframe. It does not perform semantic discovery, ID verification, relationship traversal, path analysis, clustering, counting, or factual ATLAS analysis.

### Input

Supply only an object containing an ordered `ids` list:

```json
{"ids": ["AML.TA0011"]}
```

The first ID is the anchor. `project_id`, `map_name`, focus-count limits, and URL-length limits are configured in Langflow.

Before calling it:

1. Verify every focus ID in `ATLAS Dataset Sandbox`.
2. Preserve the intended order and keep the primary anchor first.
3. Pass only the focus IDs the user requested or explicitly defined.
4. Do not add parents, children, mitigations, case studies, or other neighbors merely for context.

The component validates canonical ATLAS ID syntax and removes exact duplicates while preserving first occurrence, but it does not verify that an ID exists in the dataset.

### Output

Success:

```json
{
  "status": "success",
  "ids": ["AML.T0015"],
  "anchor": "AML.T0015",
  "focus_mode": "single_anchor",
  "duplicates_removed": [],
  "invalid_ids": [],
  "url": "https://embed.kumu.io/...",
  "iframe": "<iframe ...></iframe>"
}
```

Failure:

```json
{
  "status": "error",
  "ids": [],
  "invalid_ids": [],
  "duplicates_removed": [],
  "url": "",
  "iframe": "",
  "error": {
    "code": "...",
    "message": "..."
  }
}
```

A single ID produces a `focus=1` URL. Multiple IDs produce one outbound-hop (`out 1`) focus directive for each supplied ID. Therefore:

- Do not call the result a complete graph, complete neighborhood, all relationships, or all immediate neighbors.
- Do not infer ATLAS facts from the URL or rendered graph.
- Return the generated URL and iframe exactly as received.
- Do not claim success unless `status` is `success` and `url` is non-empty.
