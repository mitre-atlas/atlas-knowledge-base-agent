# %%
import json
import re
import ast
import pandas as pd
from pathlib import Path

# %%

DATA_DIR = Path(__file__).parent.parent / "data"
df = pd.read_csv(DATA_DIR / "atlas-nodes-04-2026.csv")

# %%
# Prefix subtechnique names with parent technique name using ": " separator

id_to_name_mapper = dict(zip(df["id"], df["name"]))


def parse_relationship(value):
    if pd.isna(value):
        return []

    if isinstance(value, list):
        return value

    text = str(value).strip()

    if not text or text == "[]":
        return []

    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass

    if "," in text:
        return [part.strip() for part in text.split(",") if part.strip()]

    return [text]


def get_parent_name(row):
    parent_techniques = parse_relationship(row.get("PARENT_TECHNIQUES"))

    is_subtechnique = (
        row["entity"] == "technique"
        and len(parent_techniques) > 0
    )

    if not is_subtechnique:
        return row["name"]

    parent_id = parent_techniques[0]
    parent_name = id_to_name_mapper.get(parent_id, parent_id)

    return f"{parent_name}: {row['name']}"


df["name"] = df.apply(get_parent_name, axis=1)

# Rebuild mapper after prefixing names.
id_to_name_mapper = dict(zip(df["id"], df["name"]))

# %%
# Create hierarchy hashtags for tactic -> technique -> subtechnique


def slugify_name(value):
    """
    Normalize names for hashtag suffixes.

    Examples:
    Initial Access -> initial-access
    Create Proxy AI Model -> create-proxy-ai-model
    Create Proxy AI Model: Train Proxy via Gathered AI Artifacts
      -> create-proxy-ai-model-train-proxy-via-gathered-ai-artifacts
    """
    text = str(value or "").strip().lower()

    # Remove AML-style prefixes if they appear in names.
    text = re.sub(r"^aml\.[a-z0-9.]+\s*[-:—]\s*", "", text, flags=re.IGNORECASE)

    # Convert separators to spaces.
    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = text.replace(":", " ")

    # Remove quotes/apostrophes.
    text = text.replace("'", "")
    text = text.replace('"', "")

    # Replace non-alphanumeric runs with hyphens.
    text = re.sub(r"[^a-z0-9]+", "-", text)

    # Collapse repeated hyphens.
    text = re.sub(r"-+", "-", text)

    return text.strip("-")


def tag(namespace, name):
    slug = slugify_name(name)
    if not slug:
        return None
    return f"#{namespace}/{slug}"


def names_from_ids(ids):
    names = []

    for item_id in ids:
        name = id_to_name_mapper.get(item_id)
        if name:
            names.append(name)

    return names


def build_hierarchy_hashtags(row):
    entity = row.get("entity")
    name = row.get("name")

    parent_tactic_ids = parse_relationship(row.get("PARENT_TACTICS"))
    parent_technique_ids = parse_relationship(row.get("PARENT_TECHNIQUES"))

    tags = []

    if entity == "tactic":
        tactic_tag = tag("tactic", name)
        if tactic_tag:
            tags.append(tactic_tag)

    elif entity == "technique":
        parent_tactic_names = names_from_ids(parent_tactic_ids)
        parent_technique_names = names_from_ids(parent_technique_ids)

        # Add all parent tactic tags, not just the first one.
        for parent_tactic_name in parent_tactic_names:
            parent_tactic_tag = tag("tactic", parent_tactic_name)
            if parent_tactic_tag:
                tags.append(parent_tactic_tag)

        if parent_technique_names:
            # Subtechnique:
            # all parent tactics, parent technique(s), subtechnique name
            for parent_technique_name in parent_technique_names:
                parent_technique_tag = tag("technique", parent_technique_name)
                if parent_technique_tag:
                    tags.append(parent_technique_tag)

            subtechnique_tag = tag("subtechnique", name)
            if subtechnique_tag:
                tags.append(subtechnique_tag)

        else:
            # Technique:
            # all parent tactics, technique name
            technique_tag = tag("technique", name)
            if technique_tag:
                tags.append(technique_tag)

    # Preserve order while deduping.
    deduped = []
    seen = set()

    for item in tags:
        if item and item not in seen:
            deduped.append(item)
            seen.add(item)

    return deduped

df["hashtags"] = df.apply(build_hierarchy_hashtags, axis=1)

# Optional string version for keyword/debug search.
df["hashtags_text"] = df["hashtags"].apply(lambda values: " ".join(values))

# If writing to CSV, serialize the list explicitly as JSON.
df["hashtags"] = df["hashtags"].apply(json.dumps)

# %%
# Basic validation

def hashtag_count_expected(row):
    entity = row.get("entity")
    parent_tactics = parse_relationship(row.get("PARENT_TACTICS"))
    parent_techniques = parse_relationship(row.get("PARENT_TECHNIQUES"))

    if entity == "tactic":
        return 1

    if entity == "technique" and parent_techniques:
        return len(parent_tactics) + len(parent_techniques) + 1

    if entity == "technique":
        return len(parent_tactics) + 1

    return None


df["_expected_hashtag_count"] = df.apply(hashtag_count_expected, axis=1)
df["_actual_hashtag_count"] = df["hashtags"].apply(lambda value: len(json.loads(value)))

validation = df[
    df["_expected_hashtag_count"].notna()
    & (df["_expected_hashtag_count"] != df["_actual_hashtag_count"])
][["id", "entity", "name", "PARENT_TACTICS", "PARENT_TECHNIQUES", "hashtags", "_expected_hashtag_count", "_actual_hashtag_count"]]

print(f"Validation mismatches: {len(validation)}")

if len(validation) > 0:
    print(validation.head(20).to_string(index=False))

# Remove validation helper columns before export.
df = df.drop(columns=["_expected_hashtag_count", "_actual_hashtag_count"])

# %%
# Save output

df.to_csv(DATA_DIR / "atlas-graph-nodes-04-2026-with-prefixed-names-and-hashtags.csv", index=False)
# %%
