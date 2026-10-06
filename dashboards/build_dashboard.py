#!/usr/bin/env python3
"""Build + publish the AI/BI (Lakeview) dashboard over the metric views.
Standalone (NOT part of the DAB) — databricks.yml is untouched.

  python3 dashboards/build_dashboard.py            # write .lvdash.json, create/update + publish
  python3 dashboards/build_dashboard.py --dry-run  # write .lvdash.json only

Published WITHOUT embedded credentials: every viewer queries as themselves, so
the Unity Catalog column masks / row filter from 14_column_masking apply per
viewer (finance sees spend, everyone else sees it masked).
"""
import json
import os
import subprocess
import sys

FQ = f'{os.environ.get("CATALOG", "aws_serverless_ws_sr_catalog")}.{os.environ.get("SCHEMA", "lumora_vendor_marketplace")}'
WAREHOUSE_ID = os.environ.get("WAREHOUSE_ID", "2cc7c1b1bd1873ce")
PROFILE = os.environ.get("DATABRICKS_PROFILE", "DEFAULT")
HERE_ = os.path.dirname(os.path.abspath(__file__))
GENIE_SPACE_ID = open(os.path.join(HERE_, "..", "genie", "space_id.txt")).read().strip()  # genie/create_space.py
DISPLAY_NAME = "Lumora Vendor Data Marketplace — Insights"
PARENT_PATH = os.environ.get("DASHBOARD_PARENT", "/Users/soumya.r@databricks.com")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(HERE, "vendor_marketplace.lvdash.json")
ID_FILE = os.path.join(HERE, ".dashboard_id")

DATASETS = [
    {"name": "ds_cov", "displayName": "Vendor coverage (mv_vendor_coverage)", "queryLines": [
        "SELECT `Vendor` AS vendor, `Data Type` AS data_type, `Region` AS region, ",
        "`Therapeutic Area` AS therapeutic_area, MEASURE(`Total Coverage`) AS total_coverage, ",
        "MEASURE(`Product Count`) AS products ",
        f"FROM {FQ}.mv_vendor_coverage GROUP BY ALL"]},
    {"name": "ds_spend", "displayName": "Contract spend (mv_contract_spend)", "queryLines": [
        "SELECT `Vendor` AS vendor, `Contract Status` AS contract_status, ",
        "`Contract End Date` AS contract_end, `Contract End Month` AS contract_end_month, ",
        "MEASURE(`Contract Count`) AS contracts, MEASURE(`Total Annual Spend`) AS annual_spend, ",
        "MEASURE(`Spend at Risk`) AS spend_at_risk ",
        f"FROM {FQ}.mv_contract_spend GROUP BY ALL"]},
    {"name": "ds_contacts", "displayName": "Vendor contacts (masked PII)", "queryLines": [
        "SELECT vendor_name, contact_name, title, contact_type, email, phone ",
        f"FROM {FQ}.vendor_contacts"]},
]


def q(dataset, fields, disaggregated=False, name="main_query"):
    return [{"name": name, "query": {"datasetName": dataset, "disaggregated": disaggregated,
                                     "fields": [{"name": n, "expression": e} for n, e in fields]}}]


def counter(name, dataset, expr, title, pos):
    return {"widget": {"name": name, "queries": q(dataset, [("v", expr)]),
                       "spec": {"version": 2, "widgetType": "counter",
                                "encodings": {"value": {"fieldName": "v", "displayName": title}},
                                "frame": {"showTitle": True, "title": title}}},
            "position": pos}


def bar(name, dataset, x, y_expr, y_title, title, pos, color=None, sort_desc=True):
    fields = [(x, f"`{x}`"), ("y", y_expr)] + ([(color, f"`{color}`")] if color else [])
    enc = {"x": {"fieldName": x, "scale": {"type": "categorical",
                                         **({"sort": {"by": "y-reversed"}} if sort_desc else {})},
                 "displayName": x.replace("_", " ").title()},
           "y": {"fieldName": "y", "scale": {"type": "quantitative"}, "displayName": y_title}}
    if color:
        enc["color"] = {"fieldName": color, "scale": {"type": "categorical"},
                        "displayName": color.replace("_", " ").title()}
    return {"widget": {"name": name, "queries": q(dataset, fields),
                       "spec": {"version": 3, "widgetType": "bar", "encodings": enc,
                                "frame": {"showTitle": True, "title": title}}},
            "position": pos}


def heatmap(name, dataset, x, y, value_expr, title, pos):
    fields = [(x, f"`{x}`"), (y, f"`{y}`"), ("v", value_expr)]
    enc = {"x": {"fieldName": x, "scale": {"type": "categorical"}, "displayName": x.replace("_", " ").title()},
           "y": {"fieldName": y, "scale": {"type": "categorical"}, "displayName": y.replace("_", " ").title()},
           "color": {"fieldName": "v", "scale": {"type": "quantitative"}, "displayName": "Vendors"}}
    return {"widget": {"name": name, "queries": q(dataset, fields),
                       "spec": {"version": 3, "widgetType": "heatmap", "encodings": enc,
                                "frame": {"showTitle": True, "title": title}}},
            "position": pos}


def table(name, dataset, cols, title, pos):
    return {"widget": {"name": name, "queries": q(dataset, [(c, f"`{c}`") for c, _ in cols], disaggregated=True),
                       "spec": {"version": 2, "widgetType": "table",
                                "encodings": {"columns": [{"fieldName": c, "displayName": d} for c, d in cols]},
                                "frame": {"showTitle": True, "title": title}}},
            "position": pos}


def multi_filter(name, dataset, field, title, pos):
    return {"widget": {"name": name, "queries": q(dataset, [(field, f"`{field}`")], name=f"f_{field}"),
                       "spec": {"version": 2, "widgetType": "filter-multi-select",
                                "encodings": {"fields": [{"fieldName": field, "displayName": title,
                                                          "queryName": f"f_{field}"}]},
                                "frame": {"showTitle": True, "title": title}}},
            "position": pos}


def text(name, lines, pos):
    return {"widget": {"name": name, "multilineTextboxSpec": {"lines": lines}}, "position": pos}


def P(x, y, w, h):
    return {"x": x, "y": y, "width": w, "height": h}


coverage_page = {
    "name": "coverage", "displayName": "Vendor coverage", "pageType": "PAGE_TYPE_CANVAS",
    "layout": [
        text("t_cov", ["## Which vendor covers what, where?",
                       "Every number here comes from the **mv_vendor_coverage** metric view — the same "
                       "measure definitions Genie uses. Filter to *HCP + Egypt* to answer the flagship question."],
             P(0, 0, 6, 2)),
        multi_filter("f_dt", "ds_cov", "data_type", "Data type", P(0, 2, 2, 1)),
        multi_filter("f_rg", "ds_cov", "region", "Region", P(2, 2, 2, 1)),
        multi_filter("f_ta", "ds_cov", "therapeutic_area", "Therapeutic area", P(4, 2, 2, 1)),
        counter("k_vendors", "ds_cov", "COUNT(DISTINCT `vendor`)", "Vendors", P(0, 3, 2, 2)),
        counter("k_cov", "ds_cov", "SUM(`total_coverage`)", "Total coverage (records)", P(2, 3, 2, 2)),
        counter("k_regions", "ds_cov", "COUNT(DISTINCT `region`)", "Regions covered", P(4, 3, 2, 2)),
        bar("b_vendor", "ds_cov", "vendor", "SUM(`total_coverage`)", "Total coverage",
            "Coverage by vendor", P(0, 5, 3, 6), color="data_type"),
        bar("b_region", "ds_cov", "region", "SUM(`total_coverage`)", "Total coverage",
            "Coverage by region", P(3, 5, 3, 6)),
        heatmap("h_dt_rg", "ds_cov", "region", "data_type", "COUNT(DISTINCT `vendor`)",
                "Vendor depth: # vendors by data type × region", P(0, 11, 6, 7)),
    ],
}

spend_page = {
    "name": "spend", "displayName": "Contracts & spend (governed)", "pageType": "PAGE_TYPE_CANVAS",
    "layout": [
        text("t_spend", ["## Contracts, renewals & spend",
                         "Contract cost is protected by a **Unity Catalog column mask**: members of "
                         "`lumora_finance` see dollar values; everyone else sees blanks. Contact email/phone "
                         "are partially masked and Commercial/Pricing contacts are row-filtered. "
                         "Same dashboard, same queries — governance is enforced per viewer."],
             P(0, 0, 6, 2)),
        counter("k_contracts", "ds_spend", "SUM(`contracts`)", "Contracts", P(0, 2, 2, 2)),
        counter("k_spend", "ds_spend", "SUM(`annual_spend`)", "Total annual spend (USD, finance only)", P(2, 2, 2, 2)),
        counter("k_risk", "ds_spend", "SUM(`spend_at_risk`)", "Spend at risk — expiring soon (finance only)", P(4, 2, 2, 2)),
        bar("b_status", "ds_spend", "contract_status", "SUM(`contracts`)", "Contracts",
            "Contracts by status", P(0, 4, 3, 5)),
        bar("b_spend", "ds_spend", "vendor", "SUM(`annual_spend`)", "Annual spend (USD)",
            "Annual spend by vendor (finance only)", P(3, 4, 3, 5)),
        table("tb_contracts", "ds_spend",
              [("vendor", "Vendor"), ("contract_status", "Status"), ("contract_end", "Contract end"),
               ("annual_spend", "Annual spend (USD)")],
              "Contract register", P(0, 9, 3, 7)),
        table("tb_contacts", "ds_contacts",
              [("vendor_name", "Vendor"), ("contact_name", "Contact"), ("title", "Title"),
               ("contact_type", "Type"), ("email", "Email"), ("phone", "Phone")],
              "Vendor contacts (PII masked)", P(3, 9, 3, 7)),
    ],
}

DASHBOARD = {
    "datasets": DATASETS,
    "pages": [coverage_page, spend_page],
    "uiSettings": {"genieSpace": {"isEnabled": True, "overrideId": GENIE_SPACE_ID,
                                  "enablementMode": "ENABLED"}},
}


def api(method, path, body):
    out = subprocess.run(["databricks", "api", method, path, "-p", PROFILE, "--json", json.dumps(body)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"{method} {path} failed: {out.stderr or out.stdout}")
    return json.loads(out.stdout or "{}")


if __name__ == "__main__":
    with open(OUT_FILE, "w") as f:
        json.dump(DASHBOARD, f, indent=2)
    print("wrote", OUT_FILE)
    if "--dry-run" in sys.argv:
        sys.exit(0)

    body = {"display_name": DISPLAY_NAME, "warehouse_id": WAREHOUSE_ID,
            "serialized_dashboard": json.dumps(DASHBOARD)}
    if os.path.exists(ID_FILE):
        dash_id = open(ID_FILE).read().strip()
        api("patch", f"/api/2.0/lakeview/dashboards/{dash_id}", body)
        print("updated", dash_id)
    else:
        dash_id = api("post", "/api/2.0/lakeview/dashboards", {**body, "parent_path": PARENT_PATH})["dashboard_id"]
        open(ID_FILE, "w").write(dash_id)
        print("created", dash_id)

    api("post", f"/api/2.0/lakeview/dashboards/{dash_id}/published",
        {"warehouse_id": WAREHOUSE_ID, "embed_credentials": False})
    print("published (viewer credentials — masks apply per viewer)")
    print(f"https://fevm-aws-serverless-ws-sr.cloud.databricks.com/dashboardsv3/{dash_id}/published")
