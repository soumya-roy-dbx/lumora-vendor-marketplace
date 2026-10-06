# end_to_end / vector_search

- **Notebook:** `notebooks/04_vector_search`
- **Task run id:** `422878619697569` · **Result:** `SUCCESS`
- **Started:** 2026-10-06 07:02:17 UTC · **Ended:** 2026-10-06 07:02:43 UTC
- **Job run:** https://fevm-aws-serverless-ws-sr.cloud.databricks.com/?o=7474651022795245#job/789028661266524/run/1002479881266291

_Exported from the job run with `databricks jobs export-run` — cell source followed by the output the cell produced in that run._

## Cell 1

```python
# =============================================================================
# 04_vector_search
#
# Build a Vector Search index over the unstructured vendor_documents so a
# retriever tool (and the Knowledge Assistant) can answer semantic questions
# like "how does AfriHealth derive HCP counts?" or "summarize MediReach's
# contract terms."
#
# Delta-sync index with Databricks-managed embeddings (databricks-gte-large-en)
# on the CDF-enabled vendor_documents table. Uses the Databricks SDK that ships
# with serverless (no extra %pip — installing databricks-vectorsearch downgrades
# protobuf on serverless and crashes the kernel).
# =============================================================================
```

## Cell 2

```python
%run ./00_config
```

## Cell 4

```python
# CATALOG / SCHEMA / VS_ENDPOINT / EMBED_MODEL / VS_INDEX come from 00_config
import time
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.vectorsearch import (
    DeltaSyncVectorIndexSpecRequest, EmbeddingSourceColumn, PipelineType, VectorIndexType)

w = WorkspaceClient()
SOURCE_TABLE = f"{FQ}.vendor_documents"
INDEX_NAME = VS_INDEX

existing = [i.name for i in w.vector_search_indexes.list_indexes(endpoint_name=VS_ENDPOINT)]
if INDEX_NAME in existing:
    print(f"Index {INDEX_NAME} already exists — triggering sync.")
    w.vector_search_indexes.sync_index(index_name=INDEX_NAME)
else:
    print(f"Creating delta-sync index {INDEX_NAME} on {VS_ENDPOINT} ...")
    w.vector_search_indexes.create_index(
        name=INDEX_NAME,
        endpoint_name=VS_ENDPOINT,
        primary_key="doc_id",
        index_type=VectorIndexType.DELTA_SYNC,
        delta_sync_index_spec=DeltaSyncVectorIndexSpecRequest(
            source_table=SOURCE_TABLE,
            pipeline_type=PipelineType.TRIGGERED,
            embedding_source_columns=[EmbeddingSourceColumn(
                name="content", embedding_model_endpoint_name=EMBED_MODEL)],
        ),
    )
    print("Create issued.")
```

**Output:**

```text
Index aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendor_docs_index already exists — triggering sync.
```

## Cell 5

```python
# Wait for the index to be ready (and fully synced), then report its status.
start = time.time()
while time.time() - start < 1500:
    idx = w.vector_search_indexes.get_index(index_name=INDEX_NAME)
    st = idx.status
    print(f"  ready={st.ready} rows_indexed={st.indexed_row_count} message={(st.message or '')[:120]}")
    if st.ready and (st.indexed_row_count or 0) > 0:
        break
    time.sleep(30)
else:
    raise TimeoutError("Index did not become ready in time.")
print("Index READY:", INDEX_NAME, "| rows indexed:", st.indexed_row_count)
```

**Output:**

```text
  ready=True rows_indexed=72 message=Index is currently online, pipeline update is pending setup of pipeline resources. Check latest status: https://fevm-aws
Index READY: aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendor_docs_index | rows indexed: 72
```

## Cell 6

```python
# Semantic retrieval test — the kind of question SQL/Genie can't answer.
res = w.vector_search_indexes.query_index(
    index_name=INDEX_NAME,
    columns=["vendor_name", "doc_type", "content"],
    query_text="How does the vendor derive HCP counts and how often is data refreshed?",
    num_results=3,
)
for row in res.result.data_array:
    print("—", row[0], "|", row[1], "| score", round(float(row[-1]), 3))
    print("  ", row[2][:180].replace("\n", " "), "...")
```

**Output:**

```text
— GlobalHCP Registry | methodology | score 0.681
   # Methodology & Coverage Notes — GlobalHCP Registry  Verified HCP master data across emerging markets.  ## Sourcing methodology GlobalHCP Registry compiles its records from a combi ...
— OncoReach | methodology | score 0.652
   # Methodology & Coverage Notes — OncoReach  Oncology HCP, HCO and trial site intelligence.  ## Sourcing methodology OncoReach compiles its records from a combination of licensed pr ...
— MediReach Analytics | methodology | score 0.649
   # Methodology & Coverage Notes — MediReach Analytics  HCP and HCO reference data with global affiliations.  ## Sourcing methodology MediReach Analytics compiles its records from a  ...
```
