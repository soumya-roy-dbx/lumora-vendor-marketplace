# Databricks App logs — lumora-data-marketplace

_Captured 2026-10-06 07:27:17 UTC with `databricks apps logs` (last 300 lines; pip-install noise removed)._

```text
2026-10-06T06:37:37Z [SYSTEM] [INFO] Starting Databricks Apps runtime...
2026-10-06T06:38:17Z [BUILD] [INFO] Starting deployment 01f1c15081881665890bcdf016e28fa4...
2026-10-06T06:38:17Z [BUILD] [INFO] Downloading source code from /Workspace/Users/e5b94b89-a734-479c-a82a-1221417aff8d/src/01f1c15081881665890bcdf016e28fa4
2026-10-06T06:38:17Z [BUILD] [INFO] Updated file: python/source_code/mas_utils.py
2026-10-06T06:38:18Z [BUILD] [INFO] Updated file: python/source_code/lakebase_utils.py
2026-10-06T06:38:18Z [BUILD] [INFO] Updated file: python/source_code/app.py
2026-10-06T06:38:18Z [BUILD] [INFO] Updated file: python/source_code/requirements.txt
2026-10-06T06:38:19Z [BUILD] Collecting databricks-sdk>=0.57.0 (from -r requirements.txt (line 2))
2026-10-06T06:38:19Z [BUILD]   Downloading databricks_sdk-0.147.0-py3-none-any.whl.metadata (44 kB)
2026-10-06T06:38:19Z [BUILD]      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 44.3/44.3 kB 1.2 MB/s eta 0:00:00
2026-10-06T06:38:19Z [BUILD] 
2026-10-06T06:38:19Z [BUILD] Collecting psycopg>=3.1.0 (from psycopg[binary]>=3.1.0->-r requirements.txt (line 3))
2026-10-06T06:38:19Z [BUILD]   Downloading psycopg-3.3.6-py3-none-any.whl.metadata (4.4 kB)
2026-10-06T06:38:19Z [BUILD] Collecting psycopg-binary==3.3.6 (from psycopg[binary]>=3.1.0->-r requirements.txt (line 3))
2026-10-06T06:38:19Z [BUILD]   Downloading psycopg_binary-3.3.6-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.7 kB)
2026-10-06T06:38:19Z [BUILD] Downloading databricks_sdk-0.147.0-py3-none-any.whl (1.1 MB)
2026-10-06T06:38:19Z [BUILD]    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.1/1.1 MB 42.0 MB/s eta 0:00:00
2026-10-06T06:38:19Z [BUILD] 
2026-10-06T06:38:19Z [BUILD] Downloading psycopg-3.3.6-py3-none-any.whl (215 kB)
2026-10-06T06:38:19Z [BUILD]    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 215.5/215.5 kB 24.9 MB/s eta 0:00:00
2026-10-06T06:38:19Z [BUILD] 
2026-10-06T06:38:19Z [BUILD] Downloading psycopg_binary-3.3.6-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.3 MB)
2026-10-06T06:38:20Z [BUILD]    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.3/5.3 MB 126.3 MB/s eta 0:00:00
2026-10-06T06:38:20Z [BUILD] 
2026-10-06T06:38:20Z [BUILD] Installing collected packages: psycopg-binary, psycopg, databricks-sdk
2026-10-06T06:38:21Z [BUILD]   Attempting uninstall: databricks-sdk
2026-10-06T06:38:21Z [BUILD]     Found existing installation: databricks-sdk 0.33.0
2026-10-06T06:38:21Z [BUILD]     Uninstalling databricks-sdk-0.33.0:
2026-10-06T06:38:21Z [BUILD]       Successfully uninstalled databricks-sdk-0.33.0
2026-10-06T06:38:21Z [BUILD] Successfully installed databricks-sdk-0.147.0 psycopg-3.3.6 psycopg-binary-3.3.6
2026-10-06T06:38:22Z [BUILD] 
[notice] A new release of pip is available: 24.0 -> 26.2.1
[notice] To update, run: python3_apps -m pip install --upgrade pip
2026-10-06T06:38:22Z [BUILD] [INFO] Requirements installed successfully.
2026-10-06T06:38:22Z [BUILD] [INFO] Starting app with command: [streamlit run app.py --server.port 8000 --server.address 0.0.0.0]
2026-10-06T06:38:23Z [APP] 
  You can now view your Streamlit app in your browser.
2026-10-06T06:38:23Z [APP] 
  URL: http://0.0.0.0:8000
2026-10-06T06:38:24Z [BUILD] [INFO] Deployment 01f1c15081881665890bcdf016e28fa4 ended in 6.640640555s
2026-10-06T06:38:24Z [BUILD] [INFO] Deployment successful
2026-10-06T06:51:39Z [BUILD] [INFO] Starting deployment 01f1c15260171f4f8260f7ba61de5fb2...
2026-10-06T06:51:39Z [APP]   Stopping...
2026-10-06T06:51:39Z [BUILD] [INFO] Downloading source code from /Workspace/Users/e5b94b89-a734-479c-a82a-1221417aff8d/src/01f1c15260171f4f8260f7ba61de5fb2
2026-10-06T06:51:40Z [BUILD] [INFO] Updated file: python/source_code/mas_utils.py
2026-10-06T06:51:40Z [BUILD] [INFO] Updated file: python/source_code/lakebase_utils.py
2026-10-06T06:51:40Z [BUILD] [INFO] Updated file: python/source_code/app.py
2026-10-06T06:51:40Z [BUILD] [INFO] Updated file: python/source_code/requirements.txt
2026-10-06T06:51:40Z [BUILD] [INFO] Requirements have not changed. Skipping installation.
2026-10-06T06:51:40Z [BUILD] [INFO] Starting app with command: [streamlit run app.py --server.port 8000 --server.address 0.0.0.0]
2026-10-06T06:51:41Z [APP] 
2026-10-06T06:51:41Z [APP]   You can now view your Streamlit app in your browser.

  URL: http://0.0.0.0:8000
2026-10-06T06:51:42Z [BUILD] [INFO] Deployment 01f1c15260171f4f8260f7ba61de5fb2 ended in 3.071950614s
2026-10-06T06:51:42Z [BUILD] [INFO] Deployment successful
```
