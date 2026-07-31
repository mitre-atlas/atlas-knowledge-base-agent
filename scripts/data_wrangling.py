import pandas as pd
from typing import Tuple, Set


# ------------------------------------------------------------
# Knowledge graph builder
# ------------------------------------------------------------
def build_knowledge_graph(
    tactics_df,
    techniques_df,
    mitigations_df,
    techniques_mitigations_df,
    casestudies_df=None,
    casestudies_techniques_df=None,
    keep_domain=False,
):
    """
    Construct unified knowledge graph.

    Parameters
    ----------
    tactics_df, techniques_df, mitigations_df : pd.DataFrame
    keep_domain : bool
        If True, preserve the 'domain' column (used by ATT&CK)

    Returns
    -------
    pd.DataFrame
    """

    nodes = build_nodes(
        tactics_df,
        techniques_df,
        mitigations_df,
        casestudies_df,
        keep_domain=keep_domain,
    )

    edges, t2t, s2t, m2t, c2t = build_edges(
        techniques_df, tactics_df, techniques_mitigations_df, casestudies_techniques_df
    )

    nodes = add_relationships(nodes, t2t, s2t, m2t, c2t)

    return nodes, edges


# ------------------------------------------------------------
# Node table builders
# ------------------------------------------------------------


def build_nodes(
    tactics_df, techniques_df, mitigations_df, casestudies_df=None, keep_domain=False
):
    """
    Construct normalized node table.

    Parameters
    ----------
    tactics_df, techniques_df, mitigations_df, casestudies_df : pd.DataFrame
    keep_domain : bool
        If True, preserve the 'domain' column (used by ATT&CK)

    Returns
    -------
    pd.DataFrame
    """

    base_cols = ["ID", "name", "description", "url"]
    if keep_domain:
        base_cols.append("domain")

    tactics = tactics_df[base_cols].rename(columns={"ID": "id"})
    tactics["entity"] = "tactic"

    techniques = techniques_df[base_cols].rename(columns={"ID": "id"})
    techniques["entity"] = "technique"

    mitigations = mitigations_df[base_cols].rename(columns={"ID": "id"})
    mitigations["entity"] = "mitigation"

    if casestudies_df is not None:
        casestudies = casestudies_df[base_cols].rename(columns={"ID": "id"})
        casestudies["entity"] = "casestudy"
        nodes = pd.concat(
            [tactics, techniques, mitigations, casestudies], ignore_index=True
        )
    else:
        nodes = pd.concat([tactics, techniques, mitigations], ignore_index=True)

    nodes["label"] = nodes["id"] + ": " + nodes["name"]

    cols = ["id", "entity", "name", "description", "url", "label"]

    if keep_domain:
        cols.append("domain")

    return nodes[cols]


# ------------------------------------------------------------
# Edge builders
# ------------------------------------------------------------


def build_tactic_to_technique_edges(techniques_df, tactics_df):
    """
    Build tactic -> technique edges.

    Handles:
    - Techniques with multiple tactics
    - Subtechniques inheriting ALL parent technique tactics
    """

    # Map tactic name -> tactic ID
    tactic_name_to_id_map = dict(zip(tactics_df["name"].str.strip(), tactics_df["ID"]))

    # Split comma-separated tactics and explode to one row per tactic
    exploded = techniques_df.assign(
        tactics=techniques_df["tactics"].str.split(",")
    ).explode("tactics")
    exploded["tactics"] = exploded["tactics"].str.strip()

    # --- Identify parent techniques vs subtechniques ---
    exploded["parent_id"] = exploded["ID"].str.replace(r"\.\d+$", "", regex=True)
    exploded["is_subtechnique"] = exploded["ID"].str.contains(r"\.\d+$")

    # --- Build mapping: parent technique -> ALL its tactics ---
    # Group ensures multiple tactics per technique are preserved
    parent_map = (
        exploded[~exploded["is_subtechnique"]]
        .groupby("ID")["tactics"]
        .agg(lambda x: list(set(x)))  # deduplicate if needed
        .to_dict()
    )

    # --- Correct subtechniques ---
    # Replace each subtechnique's tactics with its parent’s full tactic list
    exploded.loc[exploded["is_subtechnique"], "tactics"] = exploded.loc[
        exploded["is_subtechnique"], "parent_id"
    ].map(parent_map)

    # Re-explode so each row has a single tactic again
    exploded = exploded.explode("tactics")

    # Cleanup helper column
    exploded = exploded.drop(columns="parent_id")

    # --- Build edges ---
    edges = pd.DataFrame(
        {"from": exploded["tactics"].map(tactic_name_to_id_map), "to": exploded["ID"]}
    )

    edges["relationship"] = "HAS_TECHNIQUE"

    return edges.dropna().drop_duplicates().reset_index(drop=True)


def build_subtechnique_edges(techniques_df):
    """
    Build technique -> subtechnique edges.

    Works for both ATLAS and ATT&CK because both
    subtechniques end in `.###`
    """

    pattern = r"\.\d{3}$"

    mask = techniques_df["ID"].str.contains(pattern)

    subtech_id = techniques_df.loc[mask, "ID"]
    tech_id = techniques_df["ID"].copy()

    tech_id[mask] = subtech_id.str[:-4]

    edges = pd.DataFrame(
        {
            "from": tech_id,
            "to": subtech_id,
        }
    ).dropna()

    edges["relationship"] = "HAS_SUBTECHNIQUE"

    return edges.reset_index(drop=True)


def build_mitigation_to_technique_edges(techniques_mitigations_df):
    """
    Build mitigation -> technique edges.
    """

    edges = techniques_mitigations_df[["source ID", "target ID"]].rename(
        columns={"source ID": "from", "target ID": "to"}
    )

    edges["relationship"] = "MITIGATES"

    return edges.reset_index(drop=True)


def build_casestudy_to_technique_edges(casestudies_techniques_df):
    """
    Build casestudy -> technique edges.
    """
    edges = casestudies_techniques_df[["source ID", "target technique ID"]].rename(
        columns={"source ID": "from", "target technique ID": "to"}
    )

    edges["relationship"] = "DEMONSTRATES"
    return edges.reset_index(drop=True)


def build_edges(
    techniques_df,
    tactics_df,
    techniques_mitigations_df,
    casestudies_techniques_df=None,
):
    """
    Construct unified edge table.

    Parameters
    ----------
    techniques_df, tactics_df, techniques_mitigations_df, casestudies_techniques_df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """

    t2t = build_tactic_to_technique_edges(techniques_df, tactics_df)
    s2t = build_subtechnique_edges(techniques_df)
    m2t = build_mitigation_to_technique_edges(techniques_mitigations_df)

    if casestudies_techniques_df is not None:
        c2t = build_casestudy_to_technique_edges(casestudies_techniques_df)
        edges = pd.concat([t2t, s2t, m2t, c2t], ignore_index=True)
    else:
        c2t = None
        edges = pd.concat([t2t, s2t, m2t], ignore_index=True)

    return edges, t2t, s2t, m2t, c2t


# ------------------------------------------------------------
# Metadata enrichment
# ------------------------------------------------------------


def add_relationships(nodes, t2t, s2t, m2t, c2t=None):
    """
    Add parent/child relationship metadata to nodes.
    """

    tactic_to_techniques_map = t2t.groupby("from")["to"].agg(list)
    technique_to_tactics_map = t2t.groupby("to")["from"].agg(list)

    subtech_to_tech_map = s2t.groupby("to")["from"].agg(list)
    tech_to_subtech_map = s2t.groupby("from")["to"].agg(list)

    tech_to_mit_map = m2t.groupby("to")["from"].agg(list)
    mit_to_tech_map = m2t.groupby("from")["to"].agg(list)

    if c2t is not None:
        cas_to_tech_map = c2t.groupby("to")["from"].agg(list)
        tech_to_cas_map = c2t.groupby("from")["to"].agg(list)
        entities_to_tech = pd.concat([t2t, s2t, m2t, c2t])
    else:
        cas_to_tech_map = None
        tech_to_cas_map = None
        entities_to_tech = pd.concat([t2t, s2t, m2t])

    entities_to_tech_map = entities_to_tech.groupby("from")["to"].agg(list)

    nodes = nodes.copy()

    nodes["PARENT_TACTICS"] = (
        nodes["id"]
        .map(technique_to_tactics_map)
        .apply(lambda x: x if isinstance(x, list) else [])
    )

    nodes["PARENT_TECHNIQUES"] = (
        nodes["id"]
        .map(subtech_to_tech_map)
        .apply(lambda x: x if isinstance(x, list) else [])
    )

    nodes["PARENT_MITIGATIONS"] = (
        nodes["id"]
        .map(tech_to_mit_map)
        .apply(lambda x: x if isinstance(x, list) else [])
    )

    if cas_to_tech_map is not None:
        nodes["PARENT_CASESTUDIES"] = (
            nodes["id"]
            .map(cas_to_tech_map)
            .apply(lambda x: x if isinstance(x, list) else [])
        )

    nodes["CHILD_TECHNIQUES"] = (
        nodes["id"]
        .map(entities_to_tech_map)
        .apply(lambda x: x if isinstance(x, list) else [])
    )

    return nodes


# ------------------------------------------------------------
# Kumu export
# ------------------------------------------------------------


def build_kumu_tables(nodes, edges):
    """
    Prepare tables for Kumu.
    """

    kumu_nodes = nodes[["id", "entity", "name", "description", "url", "label"]].copy()

    kumu_edges = edges[["from", "to", "relationship"]].copy()

    kumu_nodes["id"] = kumu_nodes["id"].str.replace(".", "-", regex=False)
    kumu_edges["from"] = kumu_edges["from"].str.replace(".", "-", regex=False)
    kumu_edges["to"] = kumu_edges["to"].str.replace(".", "-", regex=False)

    return kumu_nodes, kumu_edges


def fix_subtechnique_tactics(df: pd.DataFrame) -> Tuple[pd.DataFrame, Set[str]]:
    """
    Ensures all subtechniques have the same PARENT_TACTICS as their parent technique.

    Returns:
        df_fixed: corrected DataFrame
        num_problematic_parents: count of parent techniques with mismatches
        problematic_parent_ids: set of those parent technique IDs
    """

    df = df.copy()

    # --- helpers ---
    def is_subtechnique(x: str) -> bool:
        return x.count(".") == 2  # AML.T####.###

    def get_parent_from_id(x: str) -> str:
        return ".".join(x.split(".")[:2])  # AML.T1234.001 -> AML.T1234

    # --- split ---
    techniques = df[(df["entity"] == "technique") & (~df["id"].apply(is_subtechnique))]

    subtechniques = df[
        (df["entity"] == "technique") & (df["id"].apply(is_subtechnique))
    ]

    # --- lookup: technique_id -> tactics ---
    tech_to_tactics = techniques.set_index("id")["PARENT_TACTICS"].to_dict()

    mismatched_parent_techniques = set()
    mismatch_indices = []

    # --- detect mismatches ---
    for idx, row in subtechniques.iterrows():
        sub_id = row["id"]

        if row["PARENT_TECHNIQUES"]:
            parent_id = row["PARENT_TECHNIQUES"][0]
        else:
            parent_id = get_parent_from_id(sub_id)

        parent_tactics = set(tech_to_tactics.get(parent_id, []))
        sub_tactics = set(row["PARENT_TACTICS"])

        if parent_tactics != sub_tactics:
            mismatched_parent_techniques.add(parent_id)
            mismatch_indices.append((idx, parent_id))

    # --- fix ---
    for idx, parent_id in mismatch_indices:
        df.at[idx, "PARENT_TACTICS"] = tech_to_tactics.get(parent_id, [])

    return df, mismatched_parent_techniques
