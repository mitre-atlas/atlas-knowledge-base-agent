# %%
# Imports
import pandas as pd
from pathlib import Path

from data_wrangling import build_knowledge_graph

# %%
# Specify version
version = "v2026-07"

# %%
# Paths
ROOT_DIR = Path(__file__).parent.parent
RAW_DIR = ROOT_DIR / f"data/raw/{version}"
PRO_DIR = ROOT_DIR / f"data/atlas-data/{version}"


# %% [markdown]
# ## ATLAS
# %%
# Load data
tactics_filepath = RAW_DIR / "atlas-tactics.xlsx"
techniques_filepath = RAW_DIR / "atlas-techniques.xlsx"
mitigations_filepath = RAW_DIR / "atlas-mitigations.xlsx"
casestudies_filepath = RAW_DIR / "atlas-case-studies.xlsx"

tactics_df = (
    pd.read_excel(tactics_filepath, sheet_name="tactics")
    .sort_values(by="ID")
    .reset_index(drop=True)
)
techniques_df = (
    pd.read_excel(techniques_filepath, sheet_name="techniques")
    .sort_values(by="ID")
    .reset_index(drop=True)
)
mitigations_df = (
    pd.read_excel(mitigations_filepath, sheet_name="mitigations")
    .sort_values(by="ID")
    .reset_index(drop=True)
)
techniques_mitigations_df = (
    pd.read_excel(mitigations_filepath, sheet_name="techniques addressed")
    .sort_values(by="source ID")
    .reset_index(drop=True)
)
casestudies_df = (
    pd.read_excel(casestudies_filepath, sheet_name="case studies")
    .sort_values(by="ID")
    .reset_index(drop=True)
)
casestudies_techniques_df = (
    pd.read_excel(casestudies_filepath, sheet_name="techniques used")
    .sort_values(by="source ID")
    .reset_index(drop=True)
)

# %%
# Build knowledge graph
atlas_nodes, atlas_edges = build_knowledge_graph(
    tactics_df,
    techniques_df,
    mitigations_df,
    techniques_mitigations_df,
    casestudies_df,
    casestudies_techniques_df,
)
atlas_nodes["tags"] = "atlas"
atlas_nodes["framework"] = "atlas"


# %%
# Kumu adjustments
kumu_nodes = atlas_nodes.copy()
kumu_edges = atlas_edges.copy()
kumu_nodes.loc[:, "id"] = kumu_nodes["id"].str.replace(".", "-")
kumu_edges.loc[:, "from"] = kumu_edges["from"].str.replace(".", "-")
kumu_edges.loc[:, "to"] = kumu_edges["to"].str.replace(".", "-")


# %%
# Save nodes and edges for Kumu
filepath = PRO_DIR / f"atlas-nodes-and-edges-kumu-{version}.xlsx"
with pd.ExcelWriter(filepath) as writer:
    kumu_nodes.to_excel(writer, sheet_name="elements", index=False)
    kumu_edges.to_excel(writer, sheet_name="connections", index=False)


# %%
# Save nodes for Langflow embedding generation
atlas_nodes.to_csv(PRO_DIR / f"atlas-nodes-{version}.csv", index=False)

# %%
