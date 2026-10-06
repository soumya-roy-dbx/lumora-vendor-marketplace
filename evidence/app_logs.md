# Databricks App logs — lumora-data-marketplace

_Captured 2026-10-06 21:54:20 UTC with `databricks apps logs` (last 300 lines; pip-install noise removed)._

```text
Databricks skills are not installed. To work with Databricks reliably, first run: databricks aitools install
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
2026-10-06T07:28:22Z [BUILD] [INFO] Starting deployment 01f1c15780fc11c2ab6b7e8690757db2...
2026-10-06T07:28:22Z [APP]   Stopping...
2026-10-06T07:28:22Z [BUILD] [INFO] Downloading source code from /Workspace/Users/e5b94b89-a734-479c-a82a-1221417aff8d/src/01f1c15780fc11c2ab6b7e8690757db2
2026-10-06T07:28:22Z [BUILD] [INFO] Updated file: python/source_code/mas_utils.py
2026-10-06T07:28:22Z [BUILD] [INFO] Updated file: python/source_code/lakebase_utils.py
2026-10-06T07:28:23Z [BUILD] [INFO] Updated file: python/source_code/app.py
2026-10-06T07:28:23Z [BUILD] [INFO] Updated file: python/source_code/requirements.txt
2026-10-06T07:28:23Z [BUILD] [INFO] Requirements have not changed. Skipping installation.
2026-10-06T07:28:23Z [BUILD] [INFO] Starting app with command: [streamlit run app.py --server.port 8000 --server.address 0.0.0.0]
2026-10-06T07:28:23Z [APP] 
  You can now view your Streamlit app in your browser.
2026-10-06T07:28:23Z [APP] 
  URL: http://0.0.0.0:8000
2026-10-06T07:28:25Z [BUILD] [INFO] Deployment 01f1c15780fc11c2ab6b7e8690757db2 ended in 2.939541962s
2026-10-06T07:28:25Z [BUILD] [INFO] Deployment successful
2026-10-06T21:40:44Z [HTTP] 75.125.237.108 - - [06/Oct/2026:21:40:43 +0000] "GET / HTTP/1.1" 302 488 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:40:49Z [HTTP] 75.125.237.108 - 77731549236306@7474651022795245 [06/Oct/2026:21:40:48 +0000] "GET / HTTP/1.1" 200 460 "https://fevm-aws-serverless-ws-sr.cloud.databricks.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:40:49Z [HTTP] 75.125.237.108 - 77731549236306@7474651022795245 [06/Oct/2026:21:40:48 +0000] "GET /static/media/SourceSansPro-Regular.0d69e5ff5e92ac64a0c9.woff2 HTTP/1.1" 200 77664 "https://lumora-data-marketplace-7474651022795245.aws.databricksapps.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:40:49Z [HTTP] 75.125.237.108 - 77731549236306@7474651022795245 [06/Oct/2026:21:40:48 +0000] "GET /static/media/SourceSansPro-SemiBold.abed79cd0df1827e18cf.woff2 HTTP/1.1" 200 77452 "https://lumora-data-marketplace-7474651022795245.aws.databricksapps.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:40:49Z [HTTP] 75.125.237.108 - 77731549236306@7474651022795245 [06/Oct/2026:21:40:48 +0000] "GET /static/css/main.5513bd04.css HTTP/1.1" 200 5235 "https://lumora-data-marketplace-7474651022795245.aws.databricksapps.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:40:49Z [HTTP] 75.125.237.108 - 77731549236306@7474651022795245 [06/Oct/2026:21:40:48 +0000] "GET /static/media/SourceSansPro-Bold.118dea98980e20a81ced.woff2 HTTP/1.1" 200 76860 "https://lumora-data-marketplace-7474651022795245.aws.databricksapps.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:40:49Z [HTTP] 75.125.237.108 - 77731549236306@7474651022795245 [06/Oct/2026:21:40:48 +0000] "GET /static/js/main.33cac65c.js HTTP/1.1" 200 1037055 "https://lumora-data-marketplace-7474651022795245.aws.databricksapps.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:40:51Z [HTTP] 75.125.237.108 - 77731549236306@7474651022795245 [06/Oct/2026:21:40:50 +0000] "GET /_stcore/host-config HTTP/1.1" 200 636 "https://lumora-data-marketplace-7474651022795245.aws.databricksapps.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:40:51Z [HTTP] 75.125.237.108 - 77731549236306@7474651022795245 [06/Oct/2026:21:40:50 +0000] "GET /_stcore/health HTTP/1.1" 200 2 "https://lumora-data-marketplace-7474651022795245.aws.databricksapps.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:40:51Z [HTTP] 75.125.237.108 - 77731549236306@7474651022795245 [06/Oct/2026:21:40:50 +0000] "GET /favicon.png HTTP/1.1" 200 1019 "https://lumora-data-marketplace-7474651022795245.aws.databricksapps.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:40:54Z [HTTP] 75.125.237.108 - 77731549236306@7474651022795245 [06/Oct/2026:21:40:53 +0000] "GET /static/js/1792.d126bbd9.chunk.js HTTP/1.1" 200 502 "https://lumora-data-marketplace-7474651022795245.aws.databricksapps.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:40:54Z [APP] LAKEBASE_TILES_LOADED rows=18 instance=lumora-marketplace-db schema=lumora
2026-10-06T21:40:56Z [APP] LAKEBASE_TILES_LOADED rows=18 instance=lumora-marketplace-db schema=lumora
2026-10-06T21:41:00Z [APP] LAKEBASE_TILES_LOADED rows=18 instance=lumora-marketplace-db schema=lumora
2026-10-06T21:41:00Z [APP] LAKEBASE_TILES_LOADED rows=18 instance=lumora-marketplace-db schema=lumora
2026-10-06T21:41:00Z [APP] 
2026-10-06T21:41:01Z [HTTP] 75.125.237.108 - 77731549236306@7474651022795245 [06/Oct/2026:21:41:00 +0000] "GET /static/js/9656.8c935274.chunk.js HTTP/1.1" 200 5996 "https://lumora-data-marketplace-7474651022795245.aws.databricksapps.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:41:01Z [HTTP] 75.125.237.108 - 77731549236306@7474651022795245 [06/Oct/2026:21:41:00 +0000] "GET /static/js/6013.b6375a8d.chunk.js HTTP/1.1" 200 4602 "https://lumora-data-marketplace-7474651022795245.aws.databricksapps.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:41:17Z [APP] LAKEBASE_TILES_LOADED rows=18 instance=lumora-marketplace-db schema=lumora
2026-10-06T21:41:19Z [HTTP] 75.125.237.108 - 77731549236306@7474651022795245 [06/Oct/2026:21:41:18 +0000] "GET /static/js/6853.a1c4fa00.chunk.js HTTP/1.1" 200 761 "https://lumora-data-marketplace-7474651022795245.aws.databricksapps.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
2026-10-06T21:41:49Z [APP] ASSISTANT_ANSWERED endpoint=mas-f66866f4-endpoint secs=31.8 q='Which vendors provide HCP data in Egypt?' answer="I'll query the Genie tool to find which vendors provide HCP (Healthcare Professional) data in Egypt. ||Vendor|hcp_coverage|\n|-|-|-|\n|0|MediReach Analytics|45429|\n|1|OncoReach|37004|\n|2|AfriHealth Data|20903| The following vendors provide HCP data in Egypt:\n\n1. **MediReach Analytics** - 45,429 HCP records\n2. **OncoReach** - 37,004 HCP records\n3. **AfriHealth Data** - 20,903 HCP records\n\nAll three v"
```
