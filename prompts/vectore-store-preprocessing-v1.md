You are generating optimized retrieval fields for an ATLAS knowledge graph entity.

Your goal is to convert a structured dataset row into:

1. a compact natural-language embedding text optimized for semantic vector retrieval
2. semantic hashtags optimized for filtered and hierarchical retrieval
3. keyword terms optimized for hybrid keyword reranking

The ATLAS Agent also has a structured Dataset Agent for exact IDs, relationships, counts, and hydration. Therefore, your output should focus on semantic meaning only, not full record reconstruction.

Return ONLY valid JSON. Do not wrap the JSON in markdown.

---

# Output Schema

Return exactly this JSON shape:

{
  "embedding_text": "...",
  "semantic_hashtags": [],
  "keyword_terms": []
}

---

# Embedding Text Philosophy

The `embedding_text` should be semantically pure.

It should answer:

“What concept, behavior, risk, objective, or defensive idea does this entity represent?”

It should NOT try to preserve every detail from the row.

The embedding text is for candidate discovery. Exact facts, IDs, relationships, URLs, and record hydration will be handled later by the Dataset Agent.

---

# Embedding Text Requirements

The `embedding_text` value MUST begin with:

<Entity Name> is a <Entity Type> ...

Write 1 to 2 clear natural-language sentences.

Target length:
- Prefer 25–75 words.
- Use up to 100 words only when needed for clarity.
- Never exceed 120 words.

The text should clearly communicate:
- what the entity is
- the core concept or behavior it represents
- its purpose, risk, defensive role, or operational meaning
- the most important domain terminology needed for semantic retrieval

DO:
- Write clear, flowing prose.
- Preserve important domain concepts and terms from the row.
- Convert fragmented technical descriptions into plain language.
- Keep the description concept-focused and semantically dense.
- Include only details that help distinguish this concept from nearby concepts.

DO NOT:
- Include AML IDs
- Include database identifiers
- Include URLs
- Include citation markers
- Include code snippets
- Include formatting artifacts
- Include hashtags
- Include raw lists of related entities
- Enumerate relationships unless they are essential to the concept
- Pad the text with background information
- Copy the source row verbatim
- Add general knowledge not present in the row

Do NOT invent or infer information not present in the row.

---

# Semantic Hashtag Requirements

The `semantic_hashtags` array should contain concise conceptual tags that help retrieve this entity.

Generate 3 to 8 semantic hashtags.

Semantic hashtags should describe concepts, risks, behaviors, domains, assets, objectives, attacks, or defenses that are explicitly supported by the row.

Use lowercase ASCII.

Every tag must:
- start with "#"
- use "/" for hierarchy
- use "_" instead of spaces
- contain only lowercase letters, numbers, underscores, hyphens, slashes, periods, or colons

Preferred namespaces:
- #concept/<concept>
- #domain/<domain>
- #risk/<risk_or_failure_mode>
- #behavior/<behavior>
- #objective/<objective>
- #asset/<asset_or_target>
- #attack/<attack_pattern>
- #defense/<defensive_concept>
- #data/<data_concept>
- #model/<model_concept>
- #system/<system_concept>

Good examples:
- #concept/prompt_injection
- #domain/large_language_models
- #risk/safeguard_bypass
- #behavior/instruction_manipulation
- #attack/data_poisoning
- #defense/input_validation
- #asset/training_data
- #model/ml_model

Do NOT generate structural tags. Structural tags will be generated later by code.

Do NOT generate tags for:
- AML IDs
- entity type
- framework name
- URLs
- parent relationships
- child relationships
- fields that are not present in the row

Do NOT invent tags based on outside knowledge.

---

# Keyword Terms Requirements

The `keyword_terms` array should contain 3 to 10 retrieval keywords or short phrases.

Keyword terms should include:
- important phrases from the entity name
- important domain terms from the description
- exact terms a user might search for
- acronyms or variants only if they appear in the row

Use plain text, not hashtags.

Good examples:
- "prompt injection"
- "large language model"
- "instruction manipulation"
- "safeguard bypass"
- "training data poisoning"

Do NOT include:
- AML IDs
- URLs
- citation markers
- long sentences
- unsupported synonyms
- generic standalone words like "attack", "technique", "system", "data", or "model" unless they are part of a meaningful phrase

---

# Content Rules

Base all output only on the provided row.

Do not use general knowledge.

Do not invent:
- names
- synonyms
- relationships
- motivations
- impacts
- mitigations
- affected systems
- technical mechanisms

If the row has limited information, produce a short embedding text and only directly supported tags and keywords.

If a phrase appears in the entity name, text, or explicitly provided fields, it may be used.

If a concept is only implied by outside knowledge, do not use it.

Keep the JSON valid.

Return no prose outside the JSON.

---

# Quality Bar

A good `embedding_text` should be short enough that every word contributes to retrieval.

A bad `embedding_text`:
- tries to summarize the whole database row
- includes IDs or relationship lists
- mixes unrelated concepts
- over-explains obvious background
- uses generic filler language
- adds facts from outside the row

A good `semantic_hashtags` list should help narrow retrieval by concept.

A bad `semantic_hashtags` list:
- duplicates structural metadata
- includes IDs
- includes entity type
- includes generic tags like #attack or #ai without a specific concept
- invents concepts not present in the row

A good `keyword_terms` list should improve exact-match and hybrid retrieval.

A bad `keyword_terms` list:
- contains full sentences
- contains unsupported synonyms
- contains IDs or URLs
- contains generic single words

---

# Example Output

{
  "embedding_text": "Large Language Model Prompt Injection is a technique that manipulates model inputs to alter a large language model’s behavior or cause it to follow unintended instructions. It represents instruction manipulation that can bypass intended safeguards or system prompts.",
  "semantic_hashtags": [
    "#concept/prompt_injection",
    "#domain/large_language_models",
    "#behavior/instruction_manipulation",
    "#risk/safeguard_bypass"
  ],
  "keyword_terms": [
    "prompt injection",
    "large language model",
    "instruction manipulation",
    "safeguard bypass",
    "system prompts"
  ]
}
