"""
Generate standalone interactive HTML panels for Part II origins-of-life outputs.

The panels are offline HTML files over the existing PNG, CSV, and JSON outputs.
They are meant as a release viewer, not as a replacement for the reproducible
Python scripts that generate the underlying data.
"""
from __future__ import annotations

import csv
import html
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs"

PAPER_ORDER = [
    ("paper_02", "Paper 2: Iron-Sulfur Redox and Mineral Constraint Scaffolds"),
    ("paper_03", "Paper 3: Magnetite Networks and Distributed Electron Transport"),
    ("paper_04", "Paper 4: Interfacial Water and Proto-Chemiosmosis"),
    ("paper_05", "Paper 5: Oscillating Constraints and Polymerization Ratchet"),
    ("paper_06", "Paper 6: Autocatalytic Closure and Chemical Memory"),
    ("paper_07", "Paper 7: Aromatic Alphabets and Homochirality"),
    ("paper_08", "Paper 8: Boundaries and Coacervate Phase Separation"),
    ("paper_09", "Paper 9: Protocell Integration and Error Thresholds"),
    ("paper_10", "Paper 10: Parasitic Threshold and Boundary Logic"),
    ("paper_11", "Paper 11: Photochemical Capture and Overload Stabilization"),
    ("paper_12", "Paper 12: Tri-Regime Bioenergetics and Falsification"),
]

STYLE = r"""
:root{--ink:#18242b;--muted:#5f6c73;--line:#c9d3d8;--bg:#f6f8f9;--paper:#fff;--blue:#286f9f;--red:#ad5149}
*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;color:var(--ink);background:var(--paper)}
header{padding:26px 34px 15px;border-bottom:1px solid var(--line);background:#fbfcfc}h1{margin:0 0 8px;font-size:26px;line-height:1.2}h2{margin:0 0 12px;font-size:18px}
p{margin:0 0 10px;line-height:1.45;color:var(--muted)}main{max-width:1240px;margin:0 auto;padding:24px 26px 40px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.panel,.controls,.note{border:1px solid var(--line);background:var(--bg);border-radius:8px;padding:15px}
.controls{margin-bottom:16px}.row{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}label{display:block;font-size:13px;color:var(--muted);margin:0 0 4px}
select{width:100%;padding:7px;border:1px solid var(--line);background:white}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:12px}
.metrics div{background:white;border:1px solid var(--line);border-radius:6px;padding:10px}.metrics b{display:block;font-size:16px;overflow-wrap:anywhere}.metrics span{font-size:12px;color:var(--muted)}
svg{width:100%;height:380px;border:1px solid var(--line);border-radius:8px;background:white}.figure{width:100%;height:500px;border:1px solid var(--line);border-radius:8px;background:white;display:grid;place-items:center;overflow:hidden}
.figure img{max-width:100%;max-height:100%;display:block}.links a{display:inline-block;margin:0 8px 8px 0;color:var(--blue)}
table{border-collapse:collapse;width:100%;font-size:12px;background:white}th,td{border:1px solid #d7dee2;padding:5px;text-align:left;vertical-align:top}th{background:#eef3f6}.tablebox{max-height:430px;overflow:auto;border:1px solid var(--line);border-radius:8px;background:white}
pre{white-space:pre-wrap;overflow:auto;background:white;border:1px solid var(--line);border-radius:8px;padding:10px;margin:0;color:#2a343a}
@media(max-width:980px){.grid,.row{grid-template-columns:1fr}.figure{height:380px}.metrics{grid-template-columns:1fr 1fr}}
"""

JS = r"""
const W=900,H=380,ML=62,MR=24,MT=24,MB=54;
function fmt(v){if(v===null||v===''||Number.isNaN(Number(v)))return 'NaN';const n=Number(v);if(Math.abs(n)>=10000||(Math.abs(n)<0.001&&n!==0))return n.toExponential(2);return n.toFixed(4).replace(/\.?0+$/,'');}
function num(v){const n=Number(v);return Number.isFinite(n)?n:null}
function clear(n){while(n.firstChild)n.removeChild(n.firstChild)}
function el(name,attrs={},text=''){const n=document.createElementNS('http://www.w3.org/2000/svg',name);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text)n.textContent=text;return n}
function metric(items){const m=document.getElementById('metrics');m.innerHTML='';items.forEach(it=>{const d=document.createElement('div');d.innerHTML=`<b>${it.value}</b><span>${it.label}</span>`;m.appendChild(d)})}
function scales(xs,ys){const xmin=Math.min(...xs),xmax=Math.max(...xs);let ymin=Math.min(...ys),ymax=Math.max(...ys);if(!Number.isFinite(ymin)){ymin=0;ymax=1}if(ymin===ymax){ymin-=1;ymax+=1}return{x:v=>ML+(v-xmin)/(xmax-xmin||1)*(W-ML-MR),y:v=>H-MB-(v-ymin)/(ymax-ymin)*(H-MT-MB),ymin,ymax}}
function axes(svg,s,xlab,ylab){svg.appendChild(el('line',{x1:ML,y1:H-MB,x2:W-MR,y2:H-MB,stroke:'#333'}));svg.appendChild(el('line',{x1:ML,y1:MT,x2:ML,y2:H-MB,stroke:'#333'}));for(let i=0;i<5;i++){const y=MT+i*(H-MT-MB)/4,val=s.ymax-(s.ymax-s.ymin)*i/4;svg.appendChild(el('text',{x:ML-9,y:y+4,'text-anchor':'end','font-size':12,fill:'#555'},fmt(val)))}svg.appendChild(el('text',{x:(W+ML-MR)/2,y:H-15,'text-anchor':'middle','font-size':13,fill:'#555'},xlab));svg.appendChild(el('text',{x:16,y:(H+MT-MB)/2,transform:`rotate(-90 16 ${(H+MT-MB)/2})`,'text-anchor':'middle','font-size':13,fill:'#555'},ylab))}
function plot(rows,xk,yk){const svg=document.getElementById('chart');clear(svg);const pts=rows.map((r,i)=>({x:num(r[xk])??i,y:num(r[yk])})).filter(p=>p.y!==null);if(!pts.length){svg.appendChild(el('text',{x:W/2,y:H/2,'text-anchor':'middle',fill:'#666'},'No numeric data for selected columns'));return}const s=scales(pts.map(p=>p.x),pts.map(p=>p.y));axes(svg,s,xk,yk);let d='';pts.forEach((p,i)=>{d+=(i?'L':'M')+s.x(p.x)+' '+s.y(p.y)+' '});svg.appendChild(el('path',{d,fill:'none',stroke:'#286f9f','stroke-width':3}));pts.forEach(p=>{const c=el('circle',{cx:s.x(p.x),cy:s.y(p.y),r:3,fill:'#ad5149'});c.appendChild(el('title',{},`${xk}: ${fmt(p.x)}\n${yk}: ${fmt(p.y)}`));svg.appendChild(c)})}
function table(rows){const box=document.getElementById('table');box.innerHTML='';if(!rows.length){box.textContent='No rows';return}const keys=Object.keys(rows[0]);const t=document.createElement('table');t.innerHTML='<thead><tr>'+keys.map(k=>`<th>${k}</th>`).join('')+'</tr></thead>';const tb=document.createElement('tbody');rows.slice(0,500).forEach(r=>{const tr=document.createElement('tr');tr.innerHTML=keys.map(k=>`<td>${r[k]}</td>`).join('');tb.appendChild(tr)});t.appendChild(tb);box.appendChild(t)}
function numericKeys(rows){if(!rows.length)return[];const keys=Object.keys(rows[0]);return keys.filter(k=>rows.some(r=>num(r[k])!==null))}
"""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def make_panel(folder: str, title: str) -> None:
    path = OUT / folder
    csv_files = sorted(path.glob("*.csv"))
    figure_files = sorted(
        p for p in path.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".pdf"}
    )
    summary_path = path / "summary.json"
    tables = {p.name: read_csv(p) for p in csv_files}
    figures = [p.name for p in figure_files]
    summary = read_json(summary_path) if summary_path.exists() else {}
    data = {"tables": tables, "figures": figures, "summary": summary}
    safe_title = html.escape(title)
    html_text = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_title}</title><style>{STYLE}</style></head>
<body><header><h1>{safe_title}</h1><p>Interactive local panel for the Part II generated diagnostics cited by this paper.</p><p class="links"><a href="../interactive_index.html">Part II interactive index</a></p></header>
<main><section class="controls"><div class="row"><div><label>Figure</label><select id="figsel"></select></div><div><label>Dataset</label><select id="datasel"></select></div><div><label>X column</label><select id="xsel"></select></div><div><label>Y column</label><select id="ysel"></select></div></div><div id="metrics" class="metrics"></div></section>
<div class="grid"><section class="panel"><h2>Figure Preview</h2><div id="figbox" class="figure"></div></section><section class="panel"><h2>Numeric Plot</h2><svg id="chart"></svg></section></div>
<section class="panel" style="margin-top:16px"><h2>Data Table</h2><div id="table" class="tablebox"></div></section>
<section class="panel" style="margin-top:16px"><h2>Summary JSON</h2><pre id="summary"></pre></section></main>
<script>const DATA={json.dumps(data)};</script><script>{JS}</script>
<script>
const figsel=document.getElementById('figsel'), datasel=document.getElementById('datasel'), xsel=document.getElementById('xsel'), ysel=document.getElementById('ysel'), figbox=document.getElementById('figbox'), summary=document.getElementById('summary');
DATA.figures.forEach(f=>{{const o=document.createElement('option');o.value=f;o.textContent=f;figsel.appendChild(o);}});
Object.keys(DATA.tables).forEach(f=>{{const o=document.createElement('option');o.value=f;o.textContent=f;datasel.appendChild(o);}});
function renderFigure(){{const f=figsel.value;figbox.innerHTML='';if(!f){{figbox.textContent='No figure files found';return}}if(f.toLowerCase().endsWith('.pdf'))figbox.innerHTML=`<object data="${{f}}" type="application/pdf"><p><a href="${{f}}">Open ${{f}}</a></p></object>`;else figbox.innerHTML=`<img src="${{f}}" alt="${{f}}">`;}}
function loadColumns(){{const rows=DATA.tables[datasel.value]||[];const keys=numericKeys(rows);xsel.innerHTML='';ysel.innerHTML='';(keys.length?keys:Object.keys(rows[0]||{{}})).forEach(k=>{{const a=document.createElement('option');a.value=k;a.textContent=k;xsel.appendChild(a);const b=document.createElement('option');b.value=k;b.textContent=k;ysel.appendChild(b);}});if(keys.length>1)ysel.value=keys[1];}}
function renderData(){{const rows=DATA.tables[datasel.value]||[];metric([{{label:'dataset',value:datasel.value||'none'}},{{label:'rows',value:rows.length}},{{label:'figures',value:DATA.figures.length}},{{label:'summary fields',value:Object.keys(DATA.summary||{{}}).length}}]);table(rows);plot(rows,xsel.value,ysel.value);summary.textContent=JSON.stringify(DATA.summary,null,2);}}
figsel.onchange=renderFigure;datasel.onchange=()=>{{loadColumns();renderData();}};xsel.onchange=renderData;ysel.onchange=renderData;renderFigure();loadColumns();renderData();
</script></body></html>
"""
    (path / "interactive_panel.html").write_text(html_text, encoding="utf-8")


def make_index() -> None:
    links = []
    for folder, title in PAPER_ORDER:
        if (OUT / folder).exists():
            links.append(
                f'<p><a href="{folder}/interactive_panel.html">{html.escape(title)}</a></p>'
            )
    html_text = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Part II Interactive Panels</title><style>{STYLE}</style></head>
<body><header><h1>Part II Interactive Panels</h1><p>Local HTML dashboards for the output-bearing origins-of-life papers.</p></header>
<main><section class="panel">{''.join(links)}</section><section class="note"><p>Panels preview existing figures, render quick charts from CSV outputs, and expose each paper's summary JSON. Paper 1 has no generated panel because it cites no generated diagnostic output.</p></section></main></body></html>
"""
    (OUT / "interactive_index.html").write_text(html_text, encoding="utf-8")


def main() -> None:
    for folder, title in PAPER_ORDER:
        if (OUT / folder).exists():
            make_panel(folder, title)
    make_index()
    print(f"Wrote Part II interactive panels under {OUT}")


if __name__ == "__main__":
    main()
