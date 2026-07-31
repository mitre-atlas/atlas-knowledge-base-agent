## Tool contract: `ATLAS Dataset Sandbox`

Callable action: `atlas_dataset_sandbox`

### Purpose

Use for:

- Exact AML.ID lookup
- Verification and hydration of vector candidates
- Exact or explicitly requested substring matching
- Field selection
- Counts, filters, rankings, groupings, and aggregates
- Parent, child, mitigation, and case-study relationships
- Reverse relationship lookup
- Dataset-wide analysis
- Paths, neighborhoods, connected components, and other multi-hop analysis derived from relationship columns

### Input and runtime

Supply only `python_code`.

The configured ATLAS CSV is already loaded as pandas DataFrame `df`. Each call runs in a fresh worker process against a fresh copy of the configured dataframe. Do not locate or reload the CSV. Do not rely on variables or mutations from previous calls.

The runtime provides:

- `df`, `pd`, and `pandas`
- `json`, `ast`, `math`, and `re`
- `RELATIONSHIP_COLUMNS`
- Preferred namespace `atlas`:
  - `atlas.info()`
  - `atlas.records(...)`
  - `atlas.select(...)`
  - `atlas.lookup(...)`
  - `atlas.hydrate(...)`
  - `atlas.relationship_ids(...)`
  - `atlas.relationship(...)`
  - `atlas.references(...)`
  - `atlas.rank_relationships(...)`
- Compatibility helpers:
  - `parse_relationship(value)`
  - `parse_ids(value)`
  - `json_ready(value)`
  - `records(frame=None, parse_relationships=True, fields=None)`
  - `select_records(entity=None, fields=None, equals=None, contains=None, sort_by=None, ascending=True, limit=None, frame=None)`
  - `hydrate_ids(ids, frame=None, fields=None)`
  - `lookup_id(aml_id, frame=None, fields=None)`
  - `relationship_ids(aml_id, column, frame=None)`
  - `hydrate_relationship(aml_id, column, frame=None, fields=None)`
  - `find_references(target_id, frame=None, columns=None, fields=None)`
  - `dataset_info(frame=None)`
  - `rank_by_relationship_count(entity, column, limit=10, fields=None, include_ties=False, frame=None)`

Prefer the `atlas` namespace for new code. The top-level helpers exist for compatibility and specialized operations.

Do not generate import statements. All supported modules and helpers are already available. Do not read or write files. Do not access the network, subprocesses, environment, runtime internals, or secrets.

Use ordinary local names such as `work`, `mask`, `items`, and `records`. The throwaway name `_` is allowed; do not create other identifiers beginning with `_`. Do not reassign `df`, `pd`, `pandas`, or `atlas`. Keep code small, deterministic, and directly tied to the ATLAS question.

### Returning a result

Use this canonical shape:

```python
# No imports. Prefer the atlas API.
result = atlas.select(
    entity="tactic",
    fields=["id", "name", "text"],
    sort_by="id",
)
```

Assign one final native JSON-compatible value to `result`. Do not print or JSON-encode it. A final expression may be captured by the runtime, but explicit `result` assignment is preferred.

Correct exact lookup:

```python
result = atlas.lookup(
    "AML.T0015",
    fields=["id", "entity", "name", "text", "description", "url"],
)
```

Correct aggregate:

```python
work = df[df["entity"].astype(str).str.lower().eq("casestudy")]
result = {
    "metric": "casestudy_count",
    "value": int(len(work)),
}
```

Incorrect:

```python
print(json.dumps(output))
```

### Output

A successful call returns native structured data:

```json
{
  "status": "success",
  "result": {
    "records": []
  },
  "dataframe": {
    "rows": 0,
    "columns": ["id", "entity", "name"]
  },
  "execution": {
    "output_bytes": 100
  }
}
```

Read ATLAS data only from the native `result` value. The outer Langflow tool message may report transport success even when this inner object has `status: "error"`; always inspect the inner status.

An unsuccessful call returns:

```json
{
  "status": "error",
  "error": {
    "code": "...",
    "message": "..."
  },
  "dataframe": {
    "rows": 0,
    "columns": []
  }
}
```

When the cause is clear, correct and retry once. For `output_too_large`, request fewer records or fields. For `timeout`, simplify the computation. Never use error text as evidence.

### Exact lookup and hydration

For exact AML.ID lookup, prefer `atlas.lookup(...)`.

For multiple IDs, prefer:

```python
result = atlas.hydrate(
    ["AML.T0015", "AML.M0003"],
    fields=["id", "entity", "name", "description", "url"],
)
```

Hydration removes duplicate requested IDs while preserving first occurrence, returns records in requested order, and reports missing or unresolved IDs when supported by the result. Preserve and report unresolved IDs.

Never use substring matching for an AML.ID.

### Matching rules

- Exact ID: exact equality only.
- Exact name: case-sensitive or case-insensitive equality according to the user’s wording.
- Substring match: only when explicitly requested or clearly disclosed.
- Literal substring: use `str.contains(term, case=False, na=False, regex=False)` unless regex behavior was explicitly requested.
- Semantic similarity: use `ATLAS Vector Store`, not pandas substring matching, unless the user explicitly asks for a textual criterion.

Prefer `atlas.select(...)` for ordinary structured filters:

```python
result = atlas.select(
    entity="tactic",
    fields=["id", "name", "text"],
    sort_by="id",
)
```

Example literal name search:

```python
mask = df["name"].astype(str).str.contains(
    "spoof",
    case=False,
    na=False,
    regex=False,
)
result = {
    "records": atlas.records(
        df.loc[mask],
        fields=["id", "entity", "name", "url"],
    )
}
```

### Relationship operations

For ranking entities by the number of linked IDs, prefer:

```python
result = atlas.rank_relationships(
    entity="tactic",
    column="CHILD_TECHNIQUES",
    limit=1,
    fields=["id", "name", "url"],
)
```

This returns a deterministic ranking sorted by relationship count descending and AML.ID ascending. Set `include_ties=True` when the user asks for all entities tied at the cutoff.

Known relationship columns:

- `PARENT_TACTICS`
- `PARENT_TECHNIQUES`
- `PARENT_MITIGATIONS`
- `PARENT_CASESTUDIES`
- `CHILD_TECHNIQUES`

Prefer the supplied operations:

```python
result = atlas.relationship_ids(
    "AML.T0015",
    "PARENT_MITIGATIONS",
)
```

```python
result = atlas.relationship(
    "AML.T0015",
    "PARENT_MITIGATIONS",
    fields=["id", "entity", "name", "description", "url"],
)
```

```python
result = atlas.references(
    "AML.T0015",
    columns=["CHILD_TECHNIQUES"],
    fields=["id", "entity", "name"],
)
```

Relationship semantics:

- Tactic `CHILD_TECHNIQUES`: techniques under the tactic.
- Technique `PARENT_TACTICS`: tactics that subsume the technique.
- Technique `PARENT_TECHNIQUES`: parent techniques for a sub-technique.
- Technique `PARENT_MITIGATIONS`: linked mitigations.
- Technique `PARENT_CASESTUDIES`: linked case studies.
- Technique `CHILD_TECHNIQUES`: sub-techniques.
- Mitigation `CHILD_TECHNIQUES`: techniques it mitigates.
- Case study `CHILD_TECHNIQUES`: techniques it demonstrates.

Do not infer absent relationships. For inverse or multi-hop questions, explicitly compute the result from parsed relationship fields.
