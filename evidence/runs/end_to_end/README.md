# Job run: [dev soumya_r] Lumora — End-to-End Data Journey

- **Job id:** `789028661266524` · **Run id:** `1002479881266291`
- **State:** `TERMINATED` / `SUCCESS`
- **Started:** 2026-10-06 06:59:25 UTC · **Ended:** 2026-10-06 07:03:34 UTC
- **Run page:** https://fevm-aws-serverless-ws-sr.cloud.databricks.com/?o=7474651022795245#job/789028661266524/run/1002479881266291

| Task | Type | Result | Started | Ended | Evidence |
|---|---|---|---|---|---|
| setup_and_generate_raw | notebook | SUCCESS | 2026-10-06 06:59:25 UTC | 2026-10-06 06:59:51 UTC | [setup_and_generate_raw.md](setup_and_generate_raw.md) |
| ingest_pipeline | pipeline | SUCCESS | 2026-10-06 06:59:51 UTC | 2026-10-06 07:00:54 UTC | pipeline `04e3d017-4b33-415b-b48c-f2c8c980d310` — see ../../pipelines/ |
| enrich_for_genie | notebook | SUCCESS | 2026-10-06 07:00:54 UTC | 2026-10-06 07:01:33 UTC | [enrich_for_genie.md](enrich_for_genie.md) |
| data_quality_rules | notebook | SUCCESS | 2026-10-06 07:01:33 UTC | 2026-10-06 07:02:41 UTC | [data_quality_rules.md](data_quality_rules.md) |
| generate_vendor_docs | notebook | SUCCESS | 2026-10-06 07:01:33 UTC | 2026-10-06 07:02:16 UTC | [generate_vendor_docs.md](generate_vendor_docs.md) |
| governance_masking | notebook | SUCCESS | 2026-10-06 07:01:33 UTC | 2026-10-06 07:02:19 UTC | [governance_masking.md](governance_masking.md) |
| sync_to_lakebase | notebook | SUCCESS | 2026-10-06 07:01:33 UTC | 2026-10-06 07:02:31 UTC | [sync_to_lakebase.md](sync_to_lakebase.md) |
| vector_search | notebook | SUCCESS | 2026-10-06 07:02:17 UTC | 2026-10-06 07:02:43 UTC | [vector_search.md](vector_search.md) |
| metric_views | notebook | SUCCESS | 2026-10-06 07:02:19 UTC | 2026-10-06 07:02:37 UTC | [metric_views.md](metric_views.md) |
| dq_pipeline | pipeline | SUCCESS | 2026-10-06 07:02:42 UTC | 2026-10-06 07:03:34 UTC | pipeline `bfee5b11-9c35-43d4-a91d-3e5bed3ffe08` — see ../../pipelines/ |
