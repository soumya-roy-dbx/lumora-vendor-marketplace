# Lakeflow pipeline: [dev soumya_r] Lumora — Ingest Vendor Catalog (Auto Loader)

- **Pipeline id:** `04e3d017-4b33-415b-b48c-f2c8c980d310` · **Serverless:** `True` · **Target:** `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace`
- **Source:** `['pipelines/ingest_vendor_catalog']`

## Recent updates

| Update id | State | Full refresh | Created |
|---|---|---|---|
| `333747c7-775c-4027-b7ef-e55901dc27dd` | COMPLETED | False | 1791269993238 |
| `82b8b83f-5436-4b9e-ad9f-f73b60740e87` | COMPLETED | False | 1791267994097 |
| `c7311349-3a04-4289-9488-24abd8d6282c` | COMPLETED | False | 1791267805657 |
| `0e5eb4a3-502f-4b72-b1cd-cb803318b677` | COMPLETED | False | 1791267448020 |

## Completed update `333747c7-775c-4027-b7ef-e55901dc27dd` — flows

| Flow / dataset | Final status | Output rows | Dropped by expectations |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.bronze_vendor_catalog` | COMPLETED | 0 — no new files (Auto Loader exactly-once) |  |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.contracts` | COMPLETED | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage` | COMPLETED | 126 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_elements` | COMPLETED | 292 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_products` | COMPLETED | 44 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.silver_vendor_catalog` | COMPLETED | 0 — no new files (Auto Loader exactly-once) |  |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendors` | COMPLETED | 18 | 0 |

### Data-quality expectations — update `333747c7-775c-4027-b7ef-e55901dc27dd` (from the event log)

| Dataset | Expectation | Passed records | Failed records |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage` | `coverage_positive_count` | 126 | 0 |

_Events in this update: 61 · ERROR-level events: 0_

## Completed update `82b8b83f-5436-4b9e-ad9f-f73b60740e87` — flows

| Flow / dataset | Final status | Output rows | Dropped by expectations |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.bronze_vendor_catalog` | COMPLETED | 0 — no new files (Auto Loader exactly-once) |  |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.contracts` | COMPLETED | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage` | COMPLETED | 126 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_elements` | COMPLETED | 292 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_products` | COMPLETED | 44 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.silver_vendor_catalog` | COMPLETED | 0 — no new files (Auto Loader exactly-once) |  |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendors` | COMPLETED | 18 | 0 |

### Data-quality expectations — update `82b8b83f-5436-4b9e-ad9f-f73b60740e87` (from the event log)

| Dataset | Expectation | Passed records | Failed records |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage` | `coverage_positive_count` | 126 | 0 |

_Events in this update: 61 · ERROR-level events: 0_

## Completed update `c7311349-3a04-4289-9488-24abd8d6282c` — flows

| Flow / dataset | Final status | Output rows | Dropped by expectations |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.bronze_vendor_catalog` | COMPLETED | 0 — no new files (Auto Loader exactly-once) |  |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.contracts` | COMPLETED | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage` | COMPLETED | 126 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_elements` | COMPLETED | 292 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_products` | COMPLETED | 44 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.silver_vendor_catalog` | COMPLETED | 0 — no new files (Auto Loader exactly-once) |  |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendors` | COMPLETED | 18 | 0 |

### Data-quality expectations — update `c7311349-3a04-4289-9488-24abd8d6282c` (from the event log)

| Dataset | Expectation | Passed records | Failed records |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage` | `coverage_positive_count` | 126 | 0 |

_Events in this update: 61 · ERROR-level events: 0_

## Completed update `0e5eb4a3-502f-4b72-b1cd-cb803318b677` — flows

| Flow / dataset | Final status | Output rows | Dropped by expectations |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.bronze_vendor_catalog` | COMPLETED | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.contracts` | COMPLETED | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage` | COMPLETED | 126 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_elements` | COMPLETED | 292 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_products` | COMPLETED | 44 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.silver_vendor_catalog` | COMPLETED | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendors` | COMPLETED | 18 | 0 |

### Data-quality expectations — update `0e5eb4a3-502f-4b72-b1cd-cb803318b677` (from the event log)

| Dataset | Expectation | Passed records | Failed records |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage` | `coverage_positive_count` | 126 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.silver_vendor_catalog` | `contract_dates_ordered` | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.silver_vendor_catalog` | `has_coverage` | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.silver_vendor_catalog` | `has_products` | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.silver_vendor_catalog` | `vendor_id_present` | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.silver_vendor_catalog` | `vendor_name_present` | 18 | 0 |

_Events in this update: 70 · ERROR-level events: 0_
