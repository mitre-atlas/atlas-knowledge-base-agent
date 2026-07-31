import ast
import json
from pathlib import Path
from typing import Any

import chromadb
from lfx.custom.custom_component.component import Component
from lfx.io import IntInput, MultilineInput, Output, StrInput
from lfx.schema.data import JSON


class ChromaDBQuery(Component):
    """Semantic retrieval over an existing ATLAS Chroma collection."""

    display_name = "ATLAS Vector Store"
    description = (
        "Find semantic ATLAS candidates. Returns flattened, deduplicated records with "
        "retrieval metadata; candidate IDs still require verification in ATLAS Dataset Sandbox."
    )
    documentation: str = "https://docs.langflow.org/components-custom-components"
    icon = "search"
    name = "ChromaDBQuery"

    inputs = [
        StrInput(
            name="collection_name",
            display_name="Collection Name",
            required=True,
        ),
        StrInput(
            name="persistence_path",
            display_name="Persistence Path",
            required=True,
        ),
        MultilineInput(
            name="queries",
            display_name="Queries",
            info=(
                "One semantic query per line. Use concise ATLAS-oriented wording and include "
                "the desired entity type when useful."
            ),
            value="",
            tool_mode=True,
            required=True,
        ),
        IntInput(
            name="n_results",
            display_name="Results Per Query",
            info="Maximum candidates to retrieve for each query line.",
            value=8,
            tool_mode=True,
        ),
        StrInput(
            name="entity_type",
            display_name="Entity Type Filter",
            info=(
                "Optional exact metadata filter: tactic, technique, mitigation, or casestudy. "
                "Leave blank when the collection's metadata is uncertain."
            ),
            value="",
            tool_mode=True,
        ),
        IntInput(
            name="max_results_per_query",
            display_name="Maximum Results Per Query",
            info="Administrative cap applied even when a larger tool value is requested.",
            value=25,
            advanced=True,
        ),
    ]

    outputs = [
        Output(
            name="results",
            display_name="Results",
            method="atlas_vector_store",
            types=["json"],
        ),
    ]

    RELATIONSHIP_COLUMNS = [
        "PARENT_TACTICS",
        "PARENT_TECHNIQUES",
        "PARENT_MITIGATIONS",
        "PARENT_CASESTUDIES",
        "CHILD_TECHNIQUES",
    ]
    ARRAY_COLUMNS = ["keywords", "hashtags", *RELATIONSHIP_COLUMNS]
    VALID_ENTITY_TYPES = {"tactic", "technique", "mitigation", "casestudy"}

    def _coerce_text(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if hasattr(value, "text") and isinstance(value.text, str):
            return value.text
        if hasattr(value, "data") and isinstance(value.data, dict):
            for key in ("text", "queries", "query"):
                if value.data.get(key):
                    return str(value.data[key])
        return str(value)

    def _parse_queries(self, value: Any) -> list[str]:
        if isinstance(value, (list, tuple, set)):
            raw_values = list(value)
        else:
            text = self._coerce_text(value).strip()
            if not text:
                return []

            raw_values: list[Any]
            try:
                parsed = json.loads(text)
            except Exception:
                parsed = None

            if isinstance(parsed, list):
                raw_values = parsed
            else:
                raw_values = text.splitlines()

        queries: list[str] = []
        seen: set[str] = set()
        for item in raw_values:
            query = str(item).strip()
            if query and query not in seen:
                seen.add(query)
                queries.append(query)
        return queries

    def _normalize_entity_type(self, value: Any) -> str | None:
        text = (
            self._coerce_text(value).strip().lower().replace("_", " ").replace("-", " ")
        )
        aliases = {
            "": None,
            "case study": "casestudy",
            "case studies": "casestudy",
            "casestudies": "casestudy",
            "tactics": "tactic",
            "techniques": "technique",
            "mitigations": "mitigation",
        }
        normalized = aliases.get(text, text)
        if normalized is not None and normalized not in self.VALID_ENTITY_TYPES:
            allowed = ", ".join(sorted(self.VALID_ENTITY_TYPES))
            raise ValueError(f"entity_type must be blank or one of: {allowed}.")
        return normalized

    def _parse_list_like(self, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, (list, tuple, set)):
            values = list(value)
        else:
            text = str(value).strip()
            if not text or text in {"[]", "null", "None", "nan", "NaN"}:
                return []
            try:
                parsed = json.loads(text)
            except Exception:
                try:
                    parsed = ast.literal_eval(text)
                except Exception:
                    parsed = None

            if isinstance(parsed, (list, tuple, set)):
                values = list(parsed)
            elif isinstance(parsed, str):
                values = [parsed]
            elif "," in text:
                values = text.split(",")
            else:
                values = [text]

        result: list[str] = []
        seen: set[str] = set()
        for item in values:
            cleaned = str(item).strip().strip("'\"")
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                result.append(cleaned)
        return result

    def _document_mapping(self, document: Any) -> dict[str, Any]:
        if isinstance(document, dict):
            return document
        if not isinstance(document, str):
            return {}
        text = document.strip()
        if not text or not (text.startswith("{") and text.endswith("}")):
            return {}
        try:
            parsed = json.loads(text)
        except Exception:
            try:
                parsed = ast.literal_eval(text)
            except Exception:
                return {}
        return parsed if isinstance(parsed, dict) else {}

    def _first_nonempty(self, *values: Any) -> str:
        for value in values:
            if value is None:
                continue
            text = str(value).strip()
            if text and text not in {"nan", "NaN", "None", "null"}:
                return text
        return ""

    def _make_record(
        self,
        metadata: dict[str, Any],
        document: Any,
        chroma_id: Any,
        query: str,
        query_index: int,
        rank: int,
        distance: Any,
    ) -> dict[str, Any]:
        document_record = self._document_mapping(document)

        # Chroma metadata is preferred when both sources contain a field.
        combined = dict(document_record)
        combined.update(metadata or {})

        entity = self._first_nonempty(combined.get("entity")).lower()
        if entity in {"case study", "case_study", "case-study"}:
            entity = "casestudy"

        document_text = document if isinstance(document, str) else ""
        record: dict[str, Any] = {
            "id": self._first_nonempty(combined.get("id"), combined.get("aml_id")),
            "entity": entity,
            "name": self._first_nonempty(combined.get("name"), combined.get("title")),
            "text": self._first_nonempty(
                combined.get("text"), document_record.get("text"), document_text
            ),
            "description": self._first_nonempty(combined.get("description")),
            "url": self._first_nonempty(combined.get("url")),
            "keywords": self._parse_list_like(combined.get("keywords")),
            "hashtags": self._parse_list_like(combined.get("hashtags")),
        }
        for column in self.RELATIONSHIP_COLUMNS:
            record[column] = self._parse_list_like(combined.get(column))

        try:
            parsed_distance = float(distance) if distance is not None else None
        except (TypeError, ValueError):
            parsed_distance = None

        record["retrieval"] = {
            "query": query,
            "query_index": query_index,
            "rank": rank,
            "distance": parsed_distance,
            "matched_queries": [query],
            "hit_count": 1,
            "chroma_ids": [str(chroma_id)] if chroma_id is not None else [],
        }
        return record

    def _merge_record(self, current: dict[str, Any], incoming: dict[str, Any]) -> None:
        for field in ("id", "entity", "name", "text", "description", "url"):
            if not current.get(field) and incoming.get(field):
                current[field] = incoming[field]

        for field in self.ARRAY_COLUMNS:
            merged = list(current.get(field, []))
            for item in incoming.get(field, []):
                if item not in merged:
                    merged.append(item)
            current[field] = merged

        current_retrieval = current["retrieval"]
        incoming_retrieval = incoming["retrieval"]
        current_retrieval["hit_count"] += 1

        for query in incoming_retrieval.get("matched_queries", []):
            if query not in current_retrieval["matched_queries"]:
                current_retrieval["matched_queries"].append(query)
        for chroma_id in incoming_retrieval.get("chroma_ids", []):
            if chroma_id not in current_retrieval["chroma_ids"]:
                current_retrieval["chroma_ids"].append(chroma_id)

        old_distance = current_retrieval.get("distance")
        new_distance = incoming_retrieval.get("distance")
        is_better = new_distance is not None and (
            old_distance is None or new_distance < old_distance
        )
        if is_better:
            for field in ("query", "query_index", "rank", "distance"):
                current_retrieval[field] = incoming_retrieval[field]

    def _get_collection(self):
        collection_name = self._coerce_text(
            getattr(self, "collection_name", None)
        ).strip()
        if not collection_name:
            raise ValueError("Collection Name is required.")

        raw_path = self._coerce_text(getattr(self, "persistence_path", None)).strip()
        if not raw_path:
            raise ValueError("Persistence Path is required.")

        persistence_path = Path(raw_path).expanduser()
        if not persistence_path.exists():
            raise ValueError("The configured Chroma persistence path does not exist.")
        if not persistence_path.is_dir():
            raise ValueError(
                "The configured Chroma persistence path is not a directory."
            )

        cache_key = (str(persistence_path.resolve()), collection_name)
        if getattr(self, "_collection_cache_key", None) != cache_key:
            client = chromadb.PersistentClient(path=cache_key[0])
            self._chroma_client = client
            self._chroma_collection = client.get_collection(name=collection_name)
            self._collection_cache_key = cache_key
        return self._chroma_collection

    def _error(self, code: str, message: str) -> JSON:
        return JSON(
            data={
                "status": "error",
                "operation": "semantic_search",
                "records": [],
                "error": {"code": code, "message": message},
            }
        )

    def atlas_vector_store(self) -> JSON:
        """Langflow tool action for semantic ATLAS retrieval."""
        return self.build_output()

    def build_output(self) -> JSON:
        try:
            query_texts = self._parse_queries(getattr(self, "queries", None))
            if not query_texts:
                return self._error(
                    "no_queries", "Provide at least one non-empty semantic query."
                )

            entity_type = self._normalize_entity_type(getattr(self, "entity_type", ""))

            try:
                requested_n = int(getattr(self, "n_results", 8))
                administrative_cap = int(getattr(self, "max_results_per_query", 25))
            except (TypeError, ValueError) as exc:
                raise ValueError("Result limits must be integers.") from exc

            administrative_cap = max(1, administrative_cap)
            requested_n = max(1, requested_n)

            collection = self._get_collection()
            collection_count = int(collection.count())
            if collection_count <= 0:
                return JSON(
                    data={
                        "status": "success",
                        "operation": "semantic_search",
                        "queries": query_texts,
                        "entity_type": entity_type,
                        "records": [],
                        "retrieval": {
                            "requested_per_query": requested_n,
                            "effective_per_query": 0,
                            "returned_candidates": 0,
                            "collection_count": 0,
                        },
                        "notes": ["The configured Chroma collection is empty."],
                    }
                )

            effective_n = min(requested_n, administrative_cap, collection_count)
            query_kwargs: dict[str, Any] = {
                "query_texts": query_texts,
                "n_results": effective_n,
                "include": ["metadatas", "documents", "distances"],
            }
            if entity_type:
                query_kwargs["where"] = {"entity": entity_type}

            raw_results = collection.query(**query_kwargs)
            documents = raw_results.get("documents") or []
            metadatas = raw_results.get("metadatas") or []
            distances = raw_results.get("distances") or []
            chroma_ids = raw_results.get("ids") or []

            records_by_key: dict[str, dict[str, Any]] = {}
            order: list[str] = []

            for query_index, query in enumerate(query_texts):
                query_documents = (
                    documents[query_index] if query_index < len(documents) else []
                )
                query_metadatas = (
                    metadatas[query_index] if query_index < len(metadatas) else []
                )
                query_distances = (
                    distances[query_index] if query_index < len(distances) else []
                )
                query_ids = (
                    chroma_ids[query_index] if query_index < len(chroma_ids) else []
                )

                hit_count = max(
                    len(query_documents),
                    len(query_metadatas),
                    len(query_distances),
                    len(query_ids),
                )
                for hit_index in range(hit_count):
                    document = (
                        query_documents[hit_index]
                        if hit_index < len(query_documents)
                        else ""
                    )
                    metadata = (
                        query_metadatas[hit_index]
                        if hit_index < len(query_metadatas)
                        else {}
                    )
                    distance = (
                        query_distances[hit_index]
                        if hit_index < len(query_distances)
                        else None
                    )
                    chroma_id = (
                        query_ids[hit_index] if hit_index < len(query_ids) else None
                    )

                    if not isinstance(metadata, dict):
                        metadata = {}

                    record = self._make_record(
                        metadata=metadata,
                        document=document,
                        chroma_id=chroma_id,
                        query=query,
                        query_index=query_index,
                        rank=hit_index + 1,
                        distance=distance,
                    )

                    # Prefer the AML.ID as the deduplication key. A Chroma document ID is
                    # retained as provenance but is never promoted to an AML.ID.
                    key = (
                        record.get("id")
                        or f"__chroma__:{chroma_id or query_index}:{hit_index}"
                    )
                    if key not in records_by_key:
                        records_by_key[key] = record
                        order.append(key)
                    else:
                        self._merge_record(records_by_key[key], record)

            records = [records_by_key[key] for key in order]
            notes = [
                "Semantic candidates only; verify selected AML.IDs in ATLAS Dataset Sandbox before presenting ATLAS facts.",
                "Chroma distance is a relative retrieval signal, not a calibrated confidence probability.",
            ]
            if requested_n > effective_n:
                notes.append(
                    f"Results per query were capped at {effective_n} by collection size or component configuration."
                )

            return JSON(
                data={
                    "status": "success",
                    "operation": "semantic_search",
                    "queries": query_texts,
                    "entity_type": entity_type,
                    "records": records,
                    "retrieval": {
                        "requested_per_query": requested_n,
                        "effective_per_query": effective_n,
                        "returned_candidates": len(records),
                        "collection_count": collection_count,
                    },
                    "notes": notes,
                }
            )

        except ValueError as exc:
            self.log(f"ATLAS vector-store validation error: {exc!s}")
            return self._error("invalid_input", str(exc))
        except Exception as exc:
            self.log(f"ATLAS vector-store query failed: {type(exc).__name__}: {exc!s}")
            return self._error(
                "query_failed",
                "The ATLAS vector search failed. Check the collection configuration and query inputs.",
            )
