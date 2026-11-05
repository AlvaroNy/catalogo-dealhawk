#!/usr/bin/env python3
"""Gera index.html (autossuficiente) a partir de data/dealhawk_walmart_all_deals.csv.

Uso:  py build.py            (só biblioteca padrão)
Fonte da verdade = este script + o CSV. Nunca edite o index.html à mão.
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
CSV_PATH = ROOT / "data" / "dealhawk_walmart_all_deals.csv"
OUT = ROOT / "index.html"
EXTRACTED_ON = "05/11/2026"

# nº da loja -> (endereço, cidade, ZIP). ZIPs obtidos no geocodificador público do
# U.S. Census (endereço -> ZIP). #4416 (Tomball Pkwy = TX-249) -> 77086;
# #752 (Fairmont Pkwy) -> Pasadena 77505; #872 (N Main) -> Houston 77009.
STORES = {
    "2257": ("13484 Northwest Fwy", "Houston", "77040"),
    "2718": ("9555 S Post Oak Rd", "Houston", "77096"),
    "3425": ("9598 Rowlett Rd", "Houston", "77075"),
    "3584": ("5405 S Rice Ave", "Houston", "77081"),
    "4416": ("13003 Tomball Pkwy", "Houston", "77086"),
    "2724": ("1107 Shaver St", "Pasadena", "77506"),
    "752": ("5200 Fairmont Pkwy", "Pasadena", "77505"),
    "872": ("1919 N Main St", "Houston", "77009"),
    "2066": ("2727 Dunvale Rd", "Houston", "77063"),
    "3640": ("1118 Silber Rd", "Houston", "77055"),
}
BADGE_CODE = {"NEW": "N", "LOWEST": "L", "PRICE ↓": "D", "PRICE ↑": "U", "STOCK ↑": "S", "STOCK ↓": "s"}


def money(s):
    return float(re.sub(r"[^0-9.]", "", s) or 0)


def main():
    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8-sig")))
    store_ids = sorted({re.search(r"#(\d+)", r["store"]).group(1) for r in rows}, key=int)
    missing = [s for s in store_ids if s not in STORES]
    if missing:
        sys.exit(f"Loja(s) sem ZIP em STORES: {missing}")
    sidx = {s: i for i, s in enumerate(store_ids)}
    stores = [{"id": s, "addr": STORES[s][0], "city": STORES[s][1], "zip": STORES[s][2]} for s in store_ids]

    data = []
    for r in rows:
        sid = re.search(r"#(\d+)", r["store"]).group(1)
        m = re.match(r"(\d+) in stock", r["stock"])
        stock = int(m.group(1)) if m else -1  # -1 = "Check stock"
        flags = "".join(BADGE_CODE.get(b.strip(), "") for b in r["badges"].split(",") if b.strip())
        opt = int(re.match(r"(\d+)", r["options"]).group(1)) if r["options"] else 0
        upc = r["upc"].lstrip("0")
        data.append([
            r["name"], sidx[sid], money(r["price"]), money(r["regular"]),
            int(re.match(r"(\d+)", r["pct"]).group(1)) if r["pct"] else 0,
            stock, r["aisle"], upc, flags, opt, r["updated"],
        ])

    payload = json.dumps({"stores": stores, "rows": data}, ensure_ascii=False, separators=(",", ":"))
    html = TEMPLATE.replace("__DATA__", payload).replace("__DATE__", EXTRACTED_ON).replace("__N__", str(len(data)))
    OUT.write_text(html, encoding="utf-8")
    print(f"OK: {len(data)} itens, {len(stores)} lojas -> {OUT.name} ({OUT.stat().st_size/1024:.0f} KB)")


TEMPLATE = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#4c1d95">
<title>Clearance Walmart — Houston</title>
<style>
:root{--ac:#6d28d9;--ac2:#4c1d95;--bg:#f4f3f8;--card:#fff;--tx:#1b1630;--mut:#6b6683;--ok:#047857;--bad:#b91c1c;--ln:#e5e2ef}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;font:15px/1.35 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--tx)}
header{background:linear-gradient(135deg,var(--ac2),var(--ac));color:#fff;padding:14px 14px 10px;padding-top:max(14px,env(safe-area-inset-top))}
header h1{margin:0;font-size:18px}header p{margin:2px 0 0;font-size:12px;opacity:.85}
.bar{position:sticky;top:0;z-index:5;background:var(--bg);padding:10px 12px 6px;border-bottom:1px solid var(--ln)}
.row{display:flex;gap:8px}
input[type=search],input[type=text],input[type=tel],select{width:100%;padding:11px 12px;border:1px solid var(--ln);border-radius:10px;font-size:16px;background:#fff;color:var(--tx)}
button{font:inherit}
.btn{border:1px solid var(--ln);background:#fff;border-radius:10px;padding:10px 12px;font-weight:600;color:var(--ac2)}
.btn.pri{background:var(--ac);border-color:var(--ac);color:#fff}
.chips{display:flex;gap:6px;overflow-x:auto;padding:6px 0 2px;scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;border:1px solid var(--ln);background:#fff;border-radius:999px;padding:7px 12px;font-size:13px;white-space:nowrap}
.chip.on{background:var(--ac);border-color:var(--ac);color:#fff}
.chip small{opacity:.7}
#panel{display:none;padding:8px 0 2px}
#panel.open{display:block}
.lbl{font-size:12px;color:var(--mut);margin:8px 0 2px;font-weight:600;text-transform:uppercase;letter-spacing:.03em}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.info{display:flex;justify-content:space-between;align-items:center;padding:8px 14px;font-size:13px;color:var(--mut)}
main{padding:0 10px 90px;display:grid;gap:8px}
@media(min-width:700px){main{grid-template-columns:repeat(auto-fill,minmax(340px,1fr))}}
.card{background:var(--card);border-radius:14px;padding:11px 12px;box-shadow:0 1px 2px rgba(30,20,60,.08);display:grid;grid-template-columns:1fr auto;gap:2px 10px}
.nm{font-weight:600;grid-column:1/3;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.pr{font-size:24px;font-weight:800;color:var(--ac2)}
.pr s{font-size:13px;font-weight:500;color:var(--mut);margin-left:6px}
.off{justify-self:end;align-self:center;background:#fee2e2;color:var(--bad);font-weight:800;border-radius:8px;padding:3px 8px}
.off.big{background:var(--bad);color:#fff}
.meta{grid-column:1/3;font-size:13px;color:var(--mut);display:flex;flex-wrap:wrap;gap:4px 12px;align-items:center}
.st{color:var(--ok);font-weight:600}.st.q{color:var(--mut);font-weight:500}
.upc{font-family:ui-monospace,Menlo,Consolas,monospace;background:#f1eefb;border-radius:6px;padding:1px 6px;border:0;color:var(--tx)}
.tag{font-size:11px;font-weight:700;border-radius:6px;padding:1px 6px;background:#ede9fe;color:var(--ac2)}
.tag.l{background:#dcfce7;color:#166534}.tag.n{background:#dbeafe;color:#1e40af}
.more{display:block;margin:12px auto;width:calc(100% - 20px);max-width:420px}
.empty{padding:40px 16px;text-align:center;color:var(--mut)}
footer{padding:16px 14px 40px;font-size:12px;color:var(--mut)}
#scan{position:fixed;inset:0;background:#000;z-index:20;display:none;flex-direction:column}
#scan.open{display:flex}
#scan video{flex:1;width:100%;object-fit:cover}
#scan .bt{padding:14px;text-align:center;color:#fff}
.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#111;color:#fff;border-radius:999px;padding:8px 16px;font-size:13px;opacity:0;transition:.2s;pointer-events:none;z-index:30}
.toast.on{opacity:1}
</style>
</head>
<body>
<header>
  <h1>Clearance Walmart — Houston</h1>
  <p>__N__ itens · 10 lojas · dados coletados em __DATE__</p>
</header>

<div class="bar">
  <div class="row">
    <input id="q" type="search" placeholder="Buscar produto…" autocomplete="off" enterkeyhint="search">
    <button class="btn" id="tgl" aria-expanded="false">Filtros</button>
  </div>
  <div class="row" style="margin-top:8px">
    <input id="upc" type="tel" inputmode="numeric" placeholder="Código de barras (UPC)" autocomplete="off">
    <button class="btn pri" id="scanBtn" hidden>📷 Ler</button>
  </div>
  <div class="chips" id="disc"></div>
  <div id="panel">
    <div class="lbl">CEP (ZIP) / loja</div>
    <input id="zip" type="tel" inputmode="numeric" maxlength="5" placeholder="ZIP da loja (ex.: 77075)">
    <div class="chips" id="storeChips" style="flex-wrap:wrap;overflow:visible"></div>
    <div class="grid2">
      <div><div class="lbl">Preço até</div>
        <select id="maxp"><option value="0">Qualquer</option><option>5</option><option>10</option><option>25</option><option>50</option><option>100</option><option>250</option></select></div>
      <div><div class="lbl">Ordenar</div>
        <select id="sort">
          <option value="pct">Maior desconto</option>
          <option value="save">Maior economia ($)</option>
          <option value="pa">Menor preço</option>
          <option value="pd">Maior preço</option>
          <option value="stock">Mais estoque</option>
          <option value="nm">Nome A–Z</option>
        </select></div>
    </div>
    <div class="lbl">Etiquetas</div>
    <div class="chips" id="tags" style="flex-wrap:wrap;overflow:visible"></div>
    <div class="row" style="margin-top:8px"><button class="btn" id="clr" style="width:100%">Limpar filtros</button></div>
  </div>
</div>

<div class="info"><span id="cnt"></span></div>
<main id="list"></main>
<button class="btn pri more" id="more" hidden>Mostrar mais</button>

<footer>
  Dados coletados manualmente do DealHawk (conta de assinante) em __DATE__, apenas para consulta pessoal.
  Preços, estoque e corredores mudam rápido e podem estar desatualizados — confirme na loja.
  Projeto independente, sem vínculo com Walmart ou DealHawk.
</footer>

<div id="scan"><video id="vid" playsinline muted></video><div class="bt">Aponte para o código de barras<br><button class="btn" id="scanX" style="margin-top:8px">Fechar</button></div></div>
<div class="toast" id="toast"></div>

<script>
const D=__DATA__;
const S=D.stores,R=D.rows;
const $=id=>document.getElementById(id);
const st={q:"",upc:"",zip:"",stores:new Set(),min:0,maxp:0,tags:new Set(),sort:"pct",shown:60};
const DISC=[0,25,50,70,80];
const TAGS={N:"Novo",L:"Menor preço",D:"Preço caiu",s:"Estoque caindo"};
const PAGE=60;
const norm=s=>s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");
const names=R.map(r=>norm(r[0]));

function chips(){
  $("disc").innerHTML=DISC.map(v=>`<button class="chip ${st.min===v?"on":""}" data-d="${v}">${v?v+"%+":"Todos"}</button>`).join("");
  const cnt=S.map(()=>0);R.forEach(r=>cnt[r[1]]++);
  $("storeChips").innerHTML=S.map((s,i)=>`<button class="chip ${st.stores.has(i)?"on":""}" data-s="${i}">${s.zip} · ${s.addr}<small> (${cnt[i]})</small></button>`).join("");
  $("tags").innerHTML=Object.entries(TAGS).map(([k,v])=>`<button class="chip ${st.tags.has(k)?"on":""}" data-t="${k}">${v}</button>`).join("");
}
function storeSet(){
  if(st.stores.size)return st.stores;
  if(st.zip){const a=new Set();S.forEach((s,i)=>{if(s.zip.startsWith(st.zip))a.add(i)});return a}
  return null;
}
function filtered(){
  const ss=storeSet(),words=norm(st.q).split(/\s+/).filter(Boolean),u=st.upc.replace(/\D/g,"").replace(/^0+/,"");
  let out=[];
  for(let i=0;i<R.length;i++){
    const r=R[i];
    if(ss&&!ss.has(r[1]))continue;
    if(r[4]<st.min)continue;
    if(st.maxp&&r[2]>st.maxp)continue;
    if(u&&!r[7].includes(u)&&!u.includes(r[7]))continue;
    if(words.length&&!words.every(w=>names[i].includes(w)))continue;
    if(st.tags.size&&![...st.tags].every(t=>r[8].includes(t)))continue;
    out.push(r);
  }
  const k={pct:(a,b)=>b[4]-a[4]||b[3]-a[3],save:(a,b)=>(b[3]-b[2])-(a[3]-a[2]),pa:(a,b)=>a[2]-b[2],pd:(a,b)=>b[2]-a[2],stock:(a,b)=>b[5]-a[5],nm:(a,b)=>a[0].localeCompare(b[0])}[st.sort];
  return out.sort(k);
}
const esc=s=>s.replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const usd=n=>"$"+(n%1?n.toFixed(2):n.toFixed(2));
function card(r){
  const s=S[r[1]],stk=r[5]>=0?`<span class="st">${r[5]} em estoque</span>`:`<span class="st q">estoque: confirmar</span>`;
  const tg=[r[8].includes("N")?'<span class="tag n">NOVO</span>':"",r[8].includes("L")?'<span class="tag l">MENOR PREÇO</span>':"",r[8].includes("D")?'<span class="tag">PREÇO ↓</span>':""].join("");
  return `<article class="card"><div class="nm">${esc(r[0])}</div>
  <div class="pr">${usd(r[2])}<s>${usd(r[3])}</s></div><div class="off ${r[4]>=70?"big":""}">-${r[4]}%</div>
  <div class="meta">${stk}${r[6]?`<span>Corredor <b>${esc(r[6])}</b></span>`:""}<span>${s.addr} · ${s.zip}</span></div>
  <div class="meta"><button class="upc" data-c="${r[7]}" title="Copiar">UPC ${r[7]}</button><span>atualizado há ${esc(r[10].replace(" ago",""))} (na coleta)</span>${tg}</div></article>`;
}
let cur=[];
function render(reset){
  if(reset)st.shown=PAGE;
  cur=filtered();
  const save=cur.reduce((a,r)=>a+(r[3]-r[2]),0);
  $("cnt").textContent=`${cur.length.toLocaleString("pt-BR")} de ${R.length.toLocaleString("pt-BR")} itens`;
  $("list").innerHTML=cur.length?cur.slice(0,st.shown).map(card).join(""):'<div class="empty">Nenhum item com esses filtros.</div>';
  $("more").hidden=cur.length<=st.shown;
  $("more").textContent=`Mostrar mais (${Math.min(PAGE,cur.length-st.shown)})`;
}
function toast(m){const t=$("toast");t.textContent=m;t.classList.add("on");setTimeout(()=>t.classList.remove("on"),1400)}

let tm;const deb=()=>{clearTimeout(tm);tm=setTimeout(()=>render(true),150)};
$("q").oninput=e=>{st.q=e.target.value;deb()};
$("upc").oninput=e=>{st.upc=e.target.value;deb()};
$("zip").oninput=e=>{e.target.value=e.target.value.replace(/\D/g,"");st.zip=e.target.value;render(true)};
$("maxp").onchange=e=>{st.maxp=+e.target.value;render(true)};
$("sort").onchange=e=>{st.sort=e.target.value;render(true)};
$("tgl").onclick=()=>{const o=$("panel").classList.toggle("open");$("tgl").setAttribute("aria-expanded",o)};
$("more").onclick=()=>{st.shown+=PAGE;render(false)};
$("clr").onclick=()=>{Object.assign(st,{q:"",upc:"",zip:"",min:0,maxp:0,sort:"pct"});st.stores.clear();st.tags.clear();
  $("q").value=$("upc").value=$("zip").value="";$("maxp").value="0";$("sort").value="pct";chips();render(true)};
document.addEventListener("click",e=>{
  const b=e.target.closest("[data-d],[data-s],[data-t],[data-c]");if(!b)return;
  if(b.dataset.d!==undefined){st.min=+b.dataset.d}
  else if(b.dataset.s!==undefined){const i=+b.dataset.s;st.stores.has(i)?st.stores.delete(i):st.stores.add(i)}
  else if(b.dataset.t!==undefined){const t=b.dataset.t;st.tags.has(t)?st.tags.delete(t):st.tags.add(t)}
  else if(b.dataset.c){navigator.clipboard&&navigator.clipboard.writeText(b.dataset.c).then(()=>toast("UPC copiado"));return}
  chips();render(true);
});

/* leitura de código de barras pela câmera (Chrome/Android; onde houver BarcodeDetector) */
if("BarcodeDetector" in window&&navigator.mediaDevices){
  $("scanBtn").hidden=false;let stream,run=false;
  const stop=()=>{run=false;$("scan").classList.remove("open");stream&&stream.getTracks().forEach(t=>t.stop())};
  $("scanX").onclick=stop;
  $("scanBtn").onclick=async()=>{
    try{
      const det=new BarcodeDetector({formats:["upc_a","upc_e","ean_13","ean_8","code_128"]});
      stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:"environment"}});
      const v=$("vid");v.srcObject=stream;await v.play();$("scan").classList.add("open");run=true;
      while(run){const c=await det.detect(v).catch(()=>[]);
        if(c.length){const code=c[0].rawValue;$("upc").value=code;st.upc=code;stop();render(true);toast("Código: "+code);break}
        await new Promise(r=>setTimeout(r,250))}
    }catch(err){stop();toast("Não foi possível abrir a câmera")}
  };
}
chips();render(true);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
