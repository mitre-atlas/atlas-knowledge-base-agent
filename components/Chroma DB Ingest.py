from lfx.custom.custom_component.component import Component
from lfx.io import StrInput, DataFrameInput, Output
from lfx.schema.data import Data
import pandas as pd
import chromadb
import json
from pathlib import Path


class ChromaDBIngest(Component):
    display_name = "ChromaDB DataFrame Upsert"
    description = "Ingest a DataFrame into ChromaDB using default embeddings."
    documentation: str = "https://docs.langflow.org/components-custom-components"
    icon = "database"
    name = "ChromaDBIngest"

    # Inputs
    inputs = [
        DataFrameInput(
            name="dataframe",
            display_name="DataFrame",
            info="The pandas DataFrame to ingest",
            tool_mode=True,
        ),
        StrInput(
            name="content_field",
            display_name="Content Field",
            info="The column in the DataFrame to embed",
            value="text",
            tool_mode=True,
        ),
        StrInput(
            name="collection_name",
            display_name="Collection Name",
            info="Name of the ChromaDB collection",
            value="langflow",
            tool_mode=True,
        ),
        StrInput(
            name="persistence_path",
            display_name="Persistence Path",
            info="Where ChromaDB should persist the collection",
            value="",
            tool_mode=True,
        ),
    ]

    # Outputs
    outputs = [
        Output(display_name="Result", name="result", method="build_output"),
    ]

    def build_output(self) -> Data:
        # Ensure persistence path exists
        persist_path = Path(self.persistence_path)
        persist_path.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        chroma_client = chromadb.PersistentClient(path=str(persist_path))

        # Get or create collection
        collection = chroma_client.get_or_create_collection(name=self.collection_name)

        # Convert DataFrame JSON-safe
        if isinstance(self.dataframe, pd.DataFrame):
            df = self.dataframe
        else:
            # Attempt to convert if passed as JSON string
            df = pd.read_json(self.dataframe)

        # Upsert into collection
        collection.upsert(
            documents=df[self.content_field].tolist(),
            ids=df["id"].tolist(),
            metadatas=json.loads(df.to_json(orient="records")),
        )

        result_msg = (
            f"Upserted {len(df)} records into collection '{self.collection_name}'."
        )
        data = Data(value=result_msg)
        self.status = data
        return data
