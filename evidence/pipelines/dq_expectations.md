# Lakeflow pipeline: [dev soumya_r] Lumora — DQ Expectations (Lakeflow)

- **Pipeline id:** `bfee5b11-9c35-43d4-a91d-3e5bed3ffe08` · **Serverless:** `True` · **Target:** `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace`
- **Source:** `['notebooks/13_dlt_quality_pipeline']`

## Recent updates

| Update id | State | Full refresh | Created |
|---|---|---|---|
| `a68d104a-ef69-42bc-83c5-029de61aede9` | COMPLETED | True | 1791270163496 |
| `3db224c8-a11e-4f94-9739-e6db8bec89c1` | COMPLETED | True | 1791268159683 |
| `225ddb31-343b-412f-8883-b47778894e8f` | COMPLETED | True | 1791267994642 |

## Completed update `a68d104a-ef69-42bc-83c5-029de61aede9` — flows

| Flow / dataset | Final status | Output rows | Dropped by expectations |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.contracts_clean` | COMPLETED | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage_clean` | COMPLETED | 98 | 28 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_elements_clean` | COMPLETED | 292 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendors_clean` | COMPLETED | 18 | 0 |

### Data-quality expectations — update `a68d104a-ef69-42bc-83c5-029de61aede9` (from the event log)

| Dataset | Expectation | Passed records | Failed records |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.contracts_clean` | `contract_dates_valid` | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage_clean` | `coverage_min_5000` | 98 | 28 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage_clean` | `coverage_positive_count` | 126 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_elements_clean` | `available_element_has_name` | 292 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendors_clean` | `vendor_has_description` | 18 | 0 |

_Events in this update: 46 · ERROR-level events: 0_

## Completed update `3db224c8-a11e-4f94-9739-e6db8bec89c1` — flows

| Flow / dataset | Final status | Output rows | Dropped by expectations |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.contracts_clean` | COMPLETED | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage_clean` | COMPLETED | 98 | 28 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_elements_clean` | COMPLETED | 292 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendors_clean` | COMPLETED | 18 | 0 |

### Data-quality expectations — update `3db224c8-a11e-4f94-9739-e6db8bec89c1` (from the event log)

| Dataset | Expectation | Passed records | Failed records |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.contracts_clean` | `contract_dates_valid` | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage_clean` | `coverage_min_5000` | 98 | 28 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage_clean` | `coverage_positive_count` | 126 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_elements_clean` | `available_element_has_name` | 292 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendors_clean` | `vendor_has_description` | 18 | 0 |

_Events in this update: 46 · ERROR-level events: 0_

## Completed update `225ddb31-343b-412f-8883-b47778894e8f` — flows

| Flow / dataset | Final status | Output rows | Dropped by expectations |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.contracts_clean` | COMPLETED | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage_clean` | COMPLETED | 98 | 28 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_elements_clean` | COMPLETED | 292 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendors_clean` | COMPLETED | 18 | 0 |

### Data-quality expectations — update `225ddb31-343b-412f-8883-b47778894e8f` (from the event log)

| Dataset | Expectation | Passed records | Failed records |
|---|---|---|---|
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.contracts_clean` | `contract_dates_valid` | 18 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage_clean` | `coverage_min_5000` | 98 | 28 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.coverage_clean` | `coverage_positive_count` | 126 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.data_elements_clean` | `available_element_has_name` | 292 | 0 |
| `aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendors_clean` | `vendor_has_description` | 18 | 0 |

_Events in this update: 46 · ERROR-level events: 0_
