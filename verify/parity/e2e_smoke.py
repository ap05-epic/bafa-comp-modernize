#!/usr/bin/env python3
"""End-to-end smoke test for the VERIFY engine -- proves run_parity.py actually works,
without the pod and without the real React app.

It serves a small *mock* of the FA Comp Summary dashboard that honours the same REST
contract, selectors, and texts as the real app (per the recon), then runs the real
`run_parity.py --screen dashboard` against it and checks all three journeys resolve
correctly (happy=PASS, no-data=PASS, backend-error=PASS).

This validates the whole chain: Playwright launch -> navigation -> route() stubbing ->
assertions -> screenshots -> report -> exit code. It does NOT test the real app (that
needs the pod); it tests that the engine and the dashboard.json config are correct.

Run:  python e2e_smoke.py        (exit 0 = engine works)
Needs: pip install playwright && python -m playwright install chromium
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
VERIFY_DIR = os.path.dirname(HERE)

# A faithful-enough mock of ManagerDashboard: same REST calls (so the stubs intercept
# them), same selectors/texts the dashboard.json asserts expect, and the same 3 states.
MOCK_HTML = """<!doctype html><html><head><meta charset="utf-8"><title>Mock FA Comp Summary</title>
<style>
 body{font-family:Arial,sans-serif} .manager-dashboard-container{padding:16px}
 .ag-theme-alpine{border:1px solid #ccc;padding:8px;margin:8px 0}
 .ag-header-cell-text{font-weight:bold;display:inline-block;margin-right:24px}
 .ag-row{padding:4px 0;border-top:1px solid #eee}
 .error-message-text{color:#a00;padding:20px}
 .disclaimer-text{color:#666;font-size:12px;margin-top:8px}
 .tag-text{background:#90ee90;padding:1px 6px;border-radius:3px}
 .export-button{margin-top:12px}
</style></head>
<body><div id="app">loading...</div>
<script>
function jget(u){return fetch(u).then(r=>{if(!r.ok){var e=new Error('http '+r.status);e.status=r.status;throw e;}return r.json();});}
function esc(s){return String(s).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}
function attr(d){try{return JSON.parse(d);}catch(e){return {};}}
function metaBy(meta,cat){return (meta.reportMetaData||[]).filter(function(m){return m.attributeCategory===cat;}).map(function(m){return attr(m.attributeDefinition);});}
function showNoData(app){app.outerHTML='<div class="manager-dashboard-container"><div class="error-message-text">There is no data for your selection.</div></div>';}
function showError(app){app.outerHTML='<div class="manager-dashboard-container"><div class="error-message-text">There was a technical issue which prevented the launch of FA Comp Summary Dashboard. Please try again later or report this to the support team.</div></div>';}
function renderDashboard(app,meta,cust,records){
  var title=(metaBy(meta,'TITLE')[0]||{}).displayText||'';
  var legends=metaBy(meta,'LEGEND'); var foots=metaBy(meta,'FOOT');
  var cols=(cust.reportCustomizationMetaData||[]).filter(function(c){return c.columnVisibilityFlag;});
  var h='<div class="manager-dashboard-container">';
  h+='<div class="table-header-container"><div class="table-header"><h2>'+esc(title)+'</h2></div></div>';
  h+='<div class="table-container"><div class="grid-container"><div class="ag-theme-alpine">';
  h+='<div class="ag-header">'+cols.map(function(c){return '<span class="ag-header-cell-text">'+esc(c.columnHeaderDescription)+'</span>';}).join('')+'</div>';
  h+='<div class="ag-center-cols-container">';
  records.forEach(function(rec){h+='<div class="ag-row">'+((rec.data||[]).map(function(d){return '<span class="ag-cell">'+esc(String(d.columnValue))+'</span>';}).join(' '))+'</div>';});
  h+='</div></div></div></div>';
  h+='<div class="footer-container"><div class="left-group">'+legends.map(function(l){return '<span class="tag-wrapper"><span class="tag-text">'+esc(l.tagValue||'')+'</span> '+esc(l.displayText||'')+'</span>';}).join(' ')+'</div>';
  h+=foots.map(function(f){return '<div class="disclaimer-container"><span class="disclaimer-text">'+esc(f.displayText||'')+'</span></div>';}).join('');
  h+='<button class="export-button">Export to Excel</button></div></div>';
  app.outerHTML=h;
}
async function main(){
  var app=document.getElementById('app');
  try{
    await jget('/BAA/api/auth/token');
    var meta=await jget('/report-meta-data/100');
    var cust=await jget('/report-customization-metadata/100');
    var reports;
    try{reports=await jget('/reports/100/202504/000/FA/AB10');}
    catch(err){return showError(app);}
    var records=(reports&&reports.records)||[];
    if(records.length===0){return showNoData(app);}
    renderDashboard(app,meta,cust,records);
  }catch(err){showError(app);}
}
main();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = MOCK_HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *args):
        pass  # quiet


def main():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    tmp = tempfile.mkdtemp(prefix="bafa-e2e-")
    out_dir = os.path.join(tmp, "out")
    os.makedirs(os.path.join(out_dir, "screenshots"), exist_ok=True)

    with open(os.path.join(VERIFY_DIR, "config.example.json"), "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    cfg["react_base_url"] = f"http://127.0.0.1:{port}"
    cfg["react_base_path"] = "/"
    cfg["output_dir"] = out_dir  # absolute -> run_parity uses it as-is
    cfg_path = os.path.join(tmp, "config.json")
    with open(cfg_path, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh)

    print(f"mock dashboard at http://127.0.0.1:{port}/  -> running the real runner against it\n")
    proc = subprocess.run(
        [sys.executable, os.path.join(HERE, "run_parity.py"), "--screen", "dashboard", "--config", cfg_path],
        capture_output=True,
        text=True,
    )
    sys.stdout.write(proc.stdout)
    if proc.stderr.strip():
        sys.stderr.write(proc.stderr)
    httpd.shutdown()

    report_path = os.path.join(out_dir, "report-dashboard.json")
    if not os.path.exists(report_path):
        print("\nE2E SMOKE FAILED: no report produced.")
        return 1
    with open(report_path, "r", encoding="utf-8") as fh:
        report = json.load(fh)

    # copy the produced report + screenshots into the kit's output/ (git-ignored) so
    # they're easy to open/share -- shows exactly what a real run looks like.
    import shutil

    kit_out = os.path.abspath(os.path.join(VERIFY_DIR, "..", "output"))
    os.makedirs(os.path.join(kit_out, "screenshots"), exist_ok=True)
    for fn in ("report-dashboard.html", "report-dashboard.json"):
        src = os.path.join(out_dir, fn)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(kit_out, fn))
    shots = os.path.join(out_dir, "screenshots")
    if os.path.isdir(shots):
        for f in os.listdir(shots):
            shutil.copy(os.path.join(shots, f), os.path.join(kit_out, "screenshots", f))
    print(f"\nartifacts -> {kit_out}  (open report-dashboard.html)")

    expected = {"happy", "validation_nodata", "backend_error"}
    got = {j["id"]: j["passed"] for j in report["journeys"]}
    all_ok = report["summary"]["all_passed"] and expected <= set(got) and all(got.get(j) for j in expected)
    print(f"\njourneys: {got}")
    print(f"runner exit code: {proc.returncode}")
    if all_ok and proc.returncode == 0:
        print("E2E SMOKE OK -- the verify engine drives a page, stubs REST, asserts all 3 paths, and reports correctly.")
        return 0
    print("E2E SMOKE FAILED -- see the journeys above and the report.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
