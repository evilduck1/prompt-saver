

// ==== Clipboard Helper (robust) ====
async function copyPromptToClipboard(p){
  const text = (typeof p === "string") ? p : (p?.prompt || p?.text || "");
  if(!text) return false;
  try{
    if(navigator.clipboard && window.isSecureContext){
      await navigator.clipboard.writeText(text);
      return true;
    }
  }catch(e){}
  try{
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    const ok = document.execCommand("copy");
    ta.remove();
    return ok;
  }catch(e){
    console.error("Clipboard copy failed", e);
    return false;
  }
}
// ==== End Clipboard Helper ====
// ==== FORCE VISIBLE PROGRESS BAR (DEBUG SAFE) ====
document.addEventListener("DOMContentLoaded", () => {
  let progressWrap = document.createElement("div");
  progressWrap.id = "progressWrap";
  progressWrap.style.cssText = `
    position: fixed;
    top: 80px;
    left: 50%;
    transform: translateX(-50%);
    width: 70%;
    background: #0f0f0f;
    border: 2px solid #ffffff;
    border-radius: 10px;
    padding: 10px;
    z-index: 10000;
    display: none;
  `;

  let progressText = document.createElement("div");
  progressText.style.cssText = "color:#ffffff;font-size:13px;margin-bottom:6px;text-align:center";
  progressText.textContent = "";

  let progressBarOuter = document.createElement("div");
  progressBarOuter.style.cssText = "width:100%;height:12px;background:#222;border-radius:8px;overflow:hidden";

  let progressBarInner = document.createElement("div");
  progressBarInner.style.cssText = "height:100%;width:0%;background:#3aa675;transition:width .3s";

  progressBarOuter.appendChild(progressBarInner);
  progressWrap.appendChild(progressText);
  progressWrap.appendChild(progressBarOuter);
  document.body.appendChild(progressWrap);

  // expose helpers
  window.startProgress = (label="Working…") => {
    progressText.textContent = label;
    progressBarInner.style.width = "0%";
    progressWrap.style.display = "block";
  };

  window.updateProgress = (pct, label) => {
    if(label) progressText.textContent = label;
    progressBarInner.style.width = Math.max(0, Math.min(100, pct)) + "%";
  };

  window.endProgress = () => {
    progressWrap.style.display = "none";
  };
});
// ==== END FORCE PROGRESS BAR ====


// ==== Progress Bar ====
let progressWrap = document.createElement("div");
progressWrap.id = "progressWrap";
progressWrap.style.cssText = `
  position: fixed;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  background: #111;
  border: 1px solid #fff;
  border-radius: 8px;
  padding: 6px 10px;
  z-index: 9999;
  display: none;
`;

let progressText = document.createElement("div");
progressText.style.cssText = "color:#fff;font-size:12px;margin-bottom:4px;text-align:center";

let progressBarOuter = document.createElement("div");
progressBarOuter.style.cssText = "width:100%;height:10px;background:#222;border-radius:6px;overflow:hidden";

let progressBarInner = document.createElement("div");
progressBarInner.style.cssText = "height:100%;width:0%;background:#3aa675;transition:width .2s";

progressBarOuter.appendChild(progressBarInner);
progressWrap.appendChild(progressText);
progressWrap.appendChild(progressBarOuter);
document.body.appendChild(progressWrap);

window.startProgress = (label="Working…") => {
  progressText.textContent = label;
  progressBarInner.style.width = "0%";
  progressWrap.style.display = "block";
};

window.updateProgress = (pct, label) => {
  if(label) progressText.textContent = label;
  progressBarInner.style.width = Math.max(0, Math.min(100, pct)) + "%";
};

window.endProgress = () => {
  progressWrap.style.display = "none";
};
// ==== End Progress Bar ====

let imageLoadToken = 0;
import { open, save, confirm } from "@tauri-apps/plugin-dialog";
import { readTextFile, writeTextFile, readFile } from "@tauri-apps/plugin-fs";
import { basename, dirname, extname, join } from "@tauri-apps/api/path";
import { listen } from "@tauri-apps/api/event";
import { invoke } from "@tauri-apps/api/core";


const app = document.getElementById("app");
app.innerHTML = `
<style>
:root{
  color-scheme: dark;
  --bg:#0b0f0e; --text:#e8e8e8; --muted:#a7a7a7;
  --panel2:rgba(0,0,0,.35);
  --border:rgba(255,255,255,.14);
  --border2:rgba(255,255,255,.20);
  --btnbg:rgba(255,255,255,.06);
  --btnhover:rgba(255,255,255,.10);
  --ui-muted: rgba(167,167,167,.65);
  --ui-muted-strong: rgba(167,167,167,.90);
}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,Arial,sans-serif;background:var(--bg);color:var(--text)}

#app{height:100vh;overflow:hidden}
.page{height:100vh;display:flex;flex-direction:column;padding:24px;box-sizing:border-box}
.top{flex:0 0 auto;position:relative;padding-bottom:12px;margin-bottom:12px}
.top:after{
  content:"";
  position:absolute;left:-24px;right:-24px;bottom:0;height:1px;
  background:linear-gradient(90deg, transparent, rgba(255,255,255,.08), transparent);
}
.list{flex:1 1 auto;overflow-y:auto;overflow-x:hidden;padding-right:6px;touch-action:pan-y}

h1{margin:0;font-size:44px}
h2{margin:0;font-size:34px}
.small{font-size:12px;color:var(--muted)}
/* UI tweak: add space between labels (red) and inputs (yellow) */
.inputs .small{ margin-bottom:8px; }
/* Right column layout: keep controls aligned and push folder button to bottom */
.imageCol{
  display:flex;
  flex-direction:column;
  align-self:stretch;
}
.fileRow{
  display:flex;
  align-items:center;
  gap:10px;
  flex-wrap:wrap;
}
.fileName{
  opacity:.85;
}
.folderBtn{
  margin-top:auto;   /* pushes to bottom of the column */
  align-self:flex-start;
}


button{
  padding:10px 16px;
  border-radius:14px;
  border:1px solid var(--ui-muted);
  background:var(--btnbg);
  color:var(--text);
  cursor:pointer;
}


#addBtn{
  font-size:18px;
  padding:12px 20px;
}
button:hover{background:var(--btnhover);border-color:var(--ui-muted-strong)}
button:active{transform:translateY(1px)}
button:focus-visible{outline:none;border-color:var(--ui-muted-strong)}
button:disabled{opacity:.55;cursor:not-allowed}
.header{
  display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:16px;margin-bottom:18px
}
.header .right{justify-self:end;display:flex;gap:12px}
.inputs{
  display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:18px
}
textarea{
  width:100%;
  min-height:140px;
  box-sizing:border-box;
  padding:14px 16px;
  border-radius:14px;
  border:1px solid var(--ui-muted);
  background:rgba(255,255,255,.04);
  color:var(--text);
  line-height:1.5;
}
textarea::placeholder{color:var(--ui-muted);opacity:1}
textarea:focus{outline:none;border-color:var(--ui-muted-strong)}

.thumb{width:100%;max-height:360px;object-fit:contain;border-radius:14px;border:1px solid #ffffff var(--border);background:#0003}
.library-head{
  display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:14px;margin:14px 0
}
.badge{
  padding:8px 14px;border-radius:999px;border:1px solid #ffffff var(--border2);
  font-size:34px;line-height:1;
  visibility:hidden; /* keep layout stable */
  white-space:nowrap;
}
.badge.is-on{ visibility:visible; }

.controls{display:flex;gap:10px;flex-wrap:wrap;justify-self:end;align-items:center}
.list{display:grid;gap:16px}
.card{
  display:grid;grid-template-columns:2fr 1.2fr;gap:16px;
  padding:16px;border-radius:18px;background:var(--panel2);border:1px solid #ffffff var(--border)
}
/* prevent subtle horizontal overflow */
.card{min-width:0}
.card > *{min-width:0}
.prompt{min-width:0}

.card-header{display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:center}
.gen{font-weight:600;font-size:14px}
.prompt{
  white-space:pre-wrap;
  line-height:1.35;
  color:var(--muted);
  margin-top:8px;
  max-height: 20.5em;
  overflow: hidden;
}
@media(max-width:900px){
  .inputs,.card,.header,.library-head{grid-template-columns:1fr}
  .header .right,.controls{justify-self:start}
}

/* fixed top library bar + scrollable content (matches mockup) */
.stickybar{flex:0 0 auto; position:relative; z-index:50;}
.stickybar .library-head{
  background: rgba(15,15,15,.82);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 12px 30px rgba(0,0,0,.45);
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.scrollArea{flex:1; min-height:0; overflow-y:auto; overflow-x:hidden; padding-top:18px; overscroll-behavior:contain;}


/* Right image pane + overlay delete */
.rightpane{position:relative;display:flex;justify-content:center;align-items:center}
.delbtn{
  appearance:none;
  border:1px solid #ffffff rgba(255,255,255,.18);
  background:rgba(139,29,29,.35);
  color:#f0f0f0;
  padding:10px 14px;
  border-radius:999px;
  font-weight:800;
  font-size:14px;
  cursor:pointer;
}
.delbtn:hover{background:rgba(179,38,38,.45)}
.delbtn:active{transform:translateY(1px)}


/* Prompt header pills */
.pillrow{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.pill{
  display:inline-flex;
  align-items:center;
  padding:8px 14px;
  border-radius:999px;
  background:rgba(255,255,255,.06);
  border:1px solid #ffffff rgba(255,255,255,.16);
  box-shadow:0 10px 24px rgba(0,0,0,.25);
  font-weight:700;
  font-size:16px;
  color:#f0f0f0;
}
.copybtn{
  appearance:none;
  border:1px solid #ffffff rgba(255,255,255,.18);
  background:rgba(255,255,255,.06);
  color:#f0f0f0;
  padding:10px 16px;
  border-radius:999px;
  font-weight:700;
  font-size:14px;
  cursor:pointer;
}
.copybtn:hover{background:rgba(255,255,255,.09)}
.copybtn:active{transform:translateY(1px)}

</style>

<div class="page">
  <div class="stickybar">
<div class="library-head">
  <div id="badge" class="badge">Unsaved Changes</div>
  <div id="status" class="small"></div>
  <div class="controls">
    <h2>Library</h2>
    <button id="exportBtn" type="button">Export Backup</button>
    <button id="importBtn" type="button">Import Backup</button>
    <button id="openBtn" type="button">Open Library</button>
    <button id="saveBtn" type="button">Save Library</button>
    <button id="optimizeBtn" type="button" style="display:none" title="Convert embedded PNGs to 512px JPEG thumbnails">Optimize Images</button>
  </div>
</div>
  </div>
  <div class="scrollArea">
  <div class="top">

<div class="header">
  <h1>Prompt Saver</h1>
  <button id="addBtn" type="button">Add Prompt</button>
  <div class="right">
  </div>
</div>

<div class="inputs">
  <div>
    <div class="small">prompt input box</div>
    <textarea id="promptInput" placeholder="Type your prompt..."></textarea>
  </div>
  <div class="imageCol">
    <div class="small">prompt image input box</div>
    <input id="imageInput" type="file" accept="image/*" style="display:none"/>
    <div class="fileRow">
      <button id="chooseFileBtn" type="button">Choose File</button>
      <span id="fileName" class="small fileName">no file selected</span>
    </div>

    <button id="addFolderBtn" class="folderBtn" type="button" title="Select a folder and import every .png inside (including subfolders)">Choose Folder (Batch Add PNGs)</button>
    <!-- input preview removed (keep only file picker) -->
  </div>
</div>


  </div>

  <div id="list" class="list"></div>
</div>
  </div>
</div>
`;

const THUMB = 512;
const QUAL = 0.85;

let lib = [];
let dirty = false;
let libraryMeta = {};
let libraryLoaded = false;
let savedCount = 0; // sticky count: last saved/loaded library
// Holds the currently-selected image for the *next* prompt (no input preview UI).
let selectedImageDataUrl = "";
let selectedImageFile = null; // original File for metadata extraction
let selectedModelName = ""; // extracted from uploaded PNG metadata (best-effort)

let activePath = null;
let activeName = "No Library File Loaded";

function uid(){ return crypto.randomUUID?.() || ("id-"+Date.now()+"-"+Math.random().toString(16).slice(2)); }
function setDirty(v){
  dirty = !!v;
  const b = document.getElementById("badge");
  if (b) b.classList.toggle("is-on", dirty);
}
function combos(t){
  let m,n=1,any=false,r=/\{([^}]+)\}/g;
  while((m=r.exec(t||""))){ any=true; n *= (m[1].split("|").map(s=>s.trim()).filter(Boolean).length || 1); }
  return any?n:1;
}
function updateStatus(prefix="Ready"){
  const saved = savedCount;
  const current = lib.length;
  const extra = dirty && current !== saved ? ` • Current: ${current}` : "";
  document.getElementById("status").textContent = `${prefix} • Prompts In Library: ${saved}${extra} • Library: ${activeName}`;
}
function normalizeItems(arr){
  if(!Array.isArray(arr)) return [];
  return arr.map(p=>{
    const text = (p?.text ?? p?.prompt ?? "").toString();
    const img  = (p?.img ?? p?.imageDataUrl ?? p?.image ?? "").toString();
    const id   = (p?.id ?? uid()).toString();
    const modelName = (p?.modelName ?? p?.model ?? p?.model_name ?? "").toString();
    return {id, text, img, modelName};
  }).filter(p => (p.text && p.text.trim()) || p.img);
}
function parseLibraryJson(obj){
  if(Array.isArray(obj)) return normalizeItems(obj);
  if(obj && Array.isArray(obj.Prompts)) return normalizeItems(obj.Prompts);
  if(obj && Array.isArray(obj.library)) return normalizeItems(obj.library);
  return [];
}

function updateOptimizeButtonVisibility(){
  const btn = document.getElementById("optimizeBtn");
  if(!btn) return;

  const anyPng = lib.some(p => typeof p.img === "string" && p.img.startsWith("data:image/png"));
  btn.style.display = anyPng ? "" : "none";
}

async function openLibrary(){
  const fp = await open({
    multiple:false,
    filters:[{name:"JSON", extensions:["json"]}]
  });
  if(!fp) return;
  await openLibraryFromPath(fp);
}

async function openLibraryFromPath(fp){
  if(typeof startProgress==="function") startProgress("Loading library…");
  if(typeof updateProgress==="function") updateProgress(5, "Opening…");
  try{
    const txt = await readTextFile(fp);
    if(typeof updateProgress==="function") updateProgress(35, "Reading file…");
    const obj = JSON.parse(txt);
    if(typeof updateProgress==="function") updateProgress(60, "Parsing library…");
    lib = parseLibraryJson(obj);
    if(typeof updateProgress==="function") updateProgress(80, "Building view…");
    libraryMeta = obj && typeof obj === "object" && !Array.isArray(obj) ? obj : {};
    libraryLoaded = true;
    activePath = fp;
    activeName = await basename(fp);
    setDirty(false);
    savedCount = lib.length;
    render();
    if(typeof updateProgress==="function") updateProgress(100, "Done");
    if(typeof endProgress==="function") setTimeout(endProgress, 250);
    updateOptimizeButtonVisibility();
    updateStatus("Library loaded");
  }catch(e){
    if(typeof endProgress==="function") endProgress();
    console.error(e);
    alert("Failed to open library");
  }
}

async function openLastLibrary(){
  try{
    const last = await invoke("get_last_library_path");
    if(last) await openLibraryFromPath(last);
  }catch{}
}

async function saveLibrary(){
  try{
    let fp = activePath;
    if(!fp){
      fp = await save({
        filters:[{name:"JSON", extensions:["json"]}],
        defaultPath:"prompt-saver-library.json"
      });
      if(!fp) return;
      activePath = fp;
      activeName = await basename(fp);
    }
    const payload = {
      ...libraryMeta,
      Prompts: lib
    };
    await writeTextFile(fp, JSON.stringify(payload, null, 2));
    setDirty(false);
    savedCount = lib.length;
    updateOptimizeButtonVisibility();
    updateStatus("Library saved");
    try { await invoke("set_last_library_path", { path: fp }); } catch {}
  }catch(e){
    console.error(e);
    alert("Failed to save library");
  }
}

function downloadJson(filename, obj){
  const blob = new Blob([JSON.stringify(obj, null, 2)], {type:"application/json"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(()=>URL.revokeObjectURL(url), 1000);
}

async function exportBackup(){
  // Exports current library as a backup JSON file (user chooses save location).
  try{
    const fp = await save({
      filters:[{name:"JSON", extensions:["json"]}],
      defaultPath:"prompt-saver-backup.json"
    });
    if(!fp) return;
    const payload = { ...libraryMeta, Prompts: lib };
    await writeTextFile(fp, JSON.stringify(payload, null, 2));
    updateStatus("Backup exported");
  }catch(e){
    console.error(e);
    alert("Failed to export backup");
  }
}

async function importBackup(){
  // Imports prompts from a chosen backup JSON, merging into current library.
  try{
    const fp = await open({
      multiple:false,
      filters:[{name:"JSON", extensions:["json"]}]
    });
    if(!fp) return;
    const txt = await readTextFile(fp);
    const obj = JSON.parse(txt);
    const incoming = parseLibraryJson(obj);

    if(!incoming.length) return alert("No prompts found in that file.");

    const ok = await confirm(`Import ${incoming.length} prompt(s) into the current library?`);
    if(!ok) return;

    // Merge (simple append)
    lib.push(...incoming.map(p => ({
      id: uid(),
      text: p.text || "",
      img: p.img || "",
      modelName: p.modelName || ""
    })));

    setDirty(true);
    render();
    updateOptimizeButtonVisibility();
    updateStatus("Backup imported");
  }catch(e){
    console.error(e);
    alert("Failed to import backup");
  }
}

// --- Image helpers
function loadImageFromBlob(blob){
  return new Promise((resolve,reject)=>{
    const url = URL.createObjectURL(blob);
    const img = new Image();
    img.onload = ()=>{
      URL.revokeObjectURL(url);
      resolve(img);
    };
    img.onerror = (e)=>{
      URL.revokeObjectURL(url);
      reject(e);
    };
    img.src = url;
  });
}

async function imgToJpg(file){
  const blob = file instanceof Blob ? file : new Blob([file], {type:"application/octet-stream"});
  const img = await loadImageFromBlob(blob);
  const w = img.naturalWidth || img.width;
  const h = img.naturalHeight || img.height;

  const scale = Math.min(1, THUMB / Math.max(w,h));
  const cw = Math.max(1, Math.round(w*scale));
  const ch = Math.max(1, Math.round(h*scale));

  const canvas = document.createElement("canvas");
  canvas.width = cw; canvas.height = ch;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(img, 0, 0, cw, ch);

  return canvas.toDataURL("image/jpeg", QUAL);
}

// --- Minimal PNG text chunk parser (tEXt / iTXt) for prompt + model extraction
function u32be(view, off){
  return view.getUint32(off, false);
}
function bytesToString(bytes){
  // Latin-1-ish decode for chunk payload; safe for JSON text metadata and standard chunks.
  let s = "";
  for(let i=0;i<bytes.length;i++) s += String.fromCharCode(bytes[i]);
  return s;
}
function tryDecodeUTF8(bytes){
  try{
    return new TextDecoder("utf-8", {fatal:false}).decode(bytes);
  }catch{
    return bytesToString(bytes);
  }
}
async function parsePngTextChunks(file){
  const buf = await file.arrayBuffer();
  const view = new DataView(buf);
  const u8 = new Uint8Array(buf);

  // PNG signature
  const sig = [137,80,78,71,13,10,26,10];
  for(let i=0;i<8;i++) if(u8[i] !== sig[i]) return {};

  let off = 8;
  const out = {};

  while(off + 8 <= u8.length){
    const len = u32be(view, off); off += 4;
    const type = bytesToString(u8.slice(off, off+4)); off += 4;

    if(off + len + 4 > u8.length) break;

    const data = u8.slice(off, off+len);
    off += len;
    off += 4; // crc

    if(type === "tEXt"){
      const idx = data.indexOf(0);
      if(idx > 0){
        const key = bytesToString(data.slice(0, idx));
        const val = bytesToString(data.slice(idx+1));
        out[key] = val;
      }
    } else if(type === "iTXt"){
      // iTXt: keyword\0 compression_flag compression_method language_tag\0 translated_keyword\0 text
      let p = 0;
      const z0 = data.indexOf(0, p); if(z0 < 0) continue;
      const key = bytesToString(data.slice(p, z0)); p = z0 + 1;
      const compressionFlag = data[p++]; // 0/1
      const compressionMethod = data[p++]; // 0
      const z1 = data.indexOf(0, p); if(z1 < 0) continue;
      const languageTag = bytesToString(data.slice(p, z1)); p = z1 + 1;
      const z2 = data.indexOf(0, p); if(z2 < 0) continue;
      const translatedKeyword = bytesToString(data.slice(p, z2)); p = z2 + 1;
      const textBytes = data.slice(p);

      // Many tools store uncompressed UTF-8 here; if compressed, we skip (keep best-effort simple).
      let val = "";
      if(compressionFlag === 0){
        val = tryDecodeUTF8(textBytes);
      } else {
        // compressed — ignore in this minimal parser
        val = "";
      }
      out[key] = val;
    }

    if(type === "IEND") break;
  }

  return out;
}

function deepFindPrompt(obj, depth=0){
  if(depth > 8 || obj == null) return "";
  if(typeof obj === "string") return "";
  if(Array.isArray(obj)){
    for(const it of obj){
      const found = deepFindPrompt(it, depth+1);
      if(found) return found;
    }
    return "";
  }
  if(typeof obj === "object"){
    // Common keys
    for(const k of ["prompt", "positive_prompt", "positive", "text", "prompt_text"]){
      if(typeof obj[k] === "string" && obj[k].trim()) return obj[k].trim();
    }
    // Node graphs sometimes store in nested "inputs"
    if(obj.inputs && typeof obj.inputs === "object"){
      const found = deepFindPrompt(obj.inputs, depth+1);
      if(found) return found;
    }
    for(const k of Object.keys(obj)){
      const found = deepFindPrompt(obj[k], depth+1);
      if(found) return found;
    }
  }
  return "";
}

function extractModelNameFromTextChunks(chunks){
  // A few common keys used by different UIs
  const keys = [
    "Model",
    "model",
    "sd_model_name",
    "model_name",
    "model_hash",
    "checkpoint",
    "Checkpoint",
    "checkpoint_name",
    "invokeai_model",
  ];
  for(const k of keys){
    if(chunks[k] && String(chunks[k]).trim()) return String(chunks[k]).trim();
  }

  // A1111 stores "parameters" blob; model often appears as "Model:" or in "Model hash:" lines depending on extensions
  if(chunks.parameters){
    const t = String(chunks.parameters);
    const m = t.match(/(?:^|\n)\s*Model:\s*([^\n]+)/i);
    if(m && m[1]) return m[1].trim();
    const m2 = t.match(/(?:^|\n)\s*Checkpoint:\s*([^\n]+)/i);
    if(m2 && m2[1]) return m2[1].trim();
  }

  // InvokeAI: sometimes JSON in invokeai_metadata
  if(chunks.invokeai_metadata){
    try{
      const meta = JSON.parse(chunks.invokeai_metadata);
      const direct = meta?.model?.name || meta?.model_name || meta?.model;
      if(typeof direct === "string" && direct.trim()) return direct.trim();
    }catch{}
  }

  return "";
}

async function extractModelNameFromFile(file){
  if(!file) return "";
  const isPng = (file.type === "image/png") || (file.name && file.name.toLowerCase().endsWith(".png"));
  if(!isPng) return "";
  const chunks = await parsePngTextChunks(file);
  return extractModelNameFromTextChunks(chunks);
}

function extractPromptFromParametersBlob(parametersText){
  // A1111 "parameters" format often:
  // <positive>
  // Negative prompt: <negative>
  // Steps: ...
  const t = String(parametersText || "").trim();
  if (!t) return "";
  const negIdx = t.toLowerCase().indexOf("\nnegative prompt:");
  const stepsIdx = t.toLowerCase().indexOf("\nsteps:");
  let cut = t.length;
  if (negIdx !== -1) cut = Math.min(cut, negIdx);
  if (stepsIdx !== -1) cut = Math.min(cut, stepsIdx);
  const pos = t.slice(0, cut).trim();
  // Some tools put "Prompt:" prefix
  return pos.replace(/^prompt:\s*/i, "").trim();
}

function extractPromptFromTextChunks(chunks){
  // Direct keys some tools write
  for (const k of ["prompt", "positive_prompt", "positive"]) {
    if (chunks[k] && String(chunks[k]).trim()) return String(chunks[k]).trim();
  }

  if (chunks.parameters) {
    const p = extractPromptFromParametersBlob(chunks.parameters);
    if (p) return p;
  }

  if (chunks.invokeai_metadata) {
    try {
      const meta = JSON.parse(chunks.invokeai_metadata);
      // Try common InvokeAI shapes
      const direct = meta?.prompt?.positive || meta?.prompt?.prompt || meta?.positive_prompt || meta?.prompt;
      if (typeof direct === "string" && direct.trim()) return direct.trim();

      // Otherwise deep search
      const found = deepFindPrompt(meta);
      if (found) return found;
    } catch {}
  }

  if (chunks.workflow) {
    try {
      const wf = JSON.parse(chunks.workflow);
      const found = deepFindPrompt(wf);
      if (found) return found;
    } catch {}
  }

  return "";
}

async function extractPromptFromFile(file){
  if (!file) return "";
  const isPng = (file.type === "image/png") || (file.name && file.name.toLowerCase().endsWith(".png"));
  if (!isPng) return "";
  const chunks = await parsePngTextChunks(file);
  return extractPromptFromTextChunks(chunks);
}


async function onImageChange(e) {
  const file = e.target.files?.[0];
  const myToken = ++imageLoadToken;

  selectedImageFile = file || null;

  const fileNameEl = document.getElementById("fileName");
  if (fileNameEl) fileNameEl.textContent = file ? (file.name || "selected") : "no file selected";

  selectedModelName = "";
  if (!file) {
    selectedImageDataUrl = "";
    selectedImageFile = null;
    return;
  }

  // Always store thumbnails as JPEG data URLs (512px max edge)
  // We still read model/prompt metadata from the original file.
  const thumbPromise = imgToJpg(file).catch(() => "");
  const modelPromise = extractModelNameFromFile(file).catch(() => "");

  const [thumbDataUrl, modelName] = await Promise.all([thumbPromise, modelPromise]);

  if (myToken !== imageLoadToken) return;

  selectedImageDataUrl = String(thumbDataUrl || "");
  selectedModelName = String(modelName || "");
}
document.getElementById("imageInput").addEventListener("change", onImageChange);

// Make the file picker look like the rest of the UI buttons
document.getElementById("chooseFileBtn")?.addEventListener("click", () => {
  document.getElementById("imageInput")?.click();
});

document.getElementById("addFolderBtn")?.addEventListener("click", batchAddPngFolder);

function hardResetImageInput() {
  const oldInput = document.getElementById("imageInput");
  const newInput = oldInput.cloneNode(true);
  oldInput.replaceWith(newInput);
  newInput.addEventListener("change", onImageChange);
  const fileNameEl = document.getElementById("fileName");
  if (fileNameEl) fileNameEl.textContent = "no file selected";
}

async function fileFromPath(path){
  // Read a file from disk (Tauri FS) and wrap it in a browser File object.
  const bytes = await readFile(path);
  const name = await basename(path);
  const ext = (await extname(path)).toLowerCase();
  const type =
    ext === "png" ? "image/png" :
    ext === "jpg" || ext === "jpeg" ? "image/jpeg" :
    ext === "webp" ? "image/webp" :
    "application/octet-stream";
  return new File([bytes], name, { type });
}

function isPngPath(path){
  return String(path || "").toLowerCase().endsWith(".png");
}

async function batchAddPngFolder(){
  const folder = await open({ directory: true });
  if (!folder) return;

  let files = [];
  try {
    files = await invoke("collect_pngs_from_folder", { folderPath: folder });
  } catch (err) {
    console.error(err);
    if (typeof endProgress === "function") endProgress();
    return alert("Folder import failed. Make sure the Rust command \'collect_pngs_from_folder\' is added on the Tauri side.");
  }

  files = (Array.isArray(files) ? files : []).filter(isPngPath);

  if (!files.length) return alert("No PNG files found in that folder.");

  
  // Progress
  if (typeof startProgress === "function") startProgress("Importing PNGs…");
  if (typeof updateProgress === "function") updateProgress(0, "Importing 0/" + files.length);
const ok = await confirm(`Found ${files.length} PNG file(s). Add them all as new items?`);
  if (!ok) return;

  let added = 0;

  for (let i = 0; i < files.length; i++){
    const filePath = files[i];

    try {
      updateStatus(`Importing ${i+1}/${files.length}`);

      const file = await fileFromPath(filePath);

      // Always store thumbnails as JPEG data URLs (512px max edge)
      const thumbPromise = imgToJpg(file).catch(() => "");
      const modelPromise = extractModelNameFromFile(file).catch(() => "");
      const promptPromise = extractPromptFromFile(file).catch(() => "");

      const [thumbDataUrl, modelName, extractedPrompt] =
        await Promise.all([thumbPromise, modelPromise, promptPromise]);

      lib.push({
        id: uid(),
        text: String(extractedPrompt || "").trim(),
        img: String(thumbDataUrl || ""),
        modelName: String(modelName || "")
      });

      added++;

      
      if (typeof updateProgress === "function") {
        const pct = Math.round(((i + 1) / files.length) * 100);
        updateProgress(pct, `Importing ${i + 1}/${files.length}`);
      }
// Light UI refresh every 25 items (keeps app responsive)
      if ((i+1) % 25 === 0){
        render();
      }
    } catch (err) {
      console.warn("Failed importing", filePath, err);
    }
  }

  if (added > 0) {
    setDirty(true);
    render();
    updateStatus(`Imported ${added} image(s)`);
  } else {
    updateStatus("Ready");
    alert("No images were imported (all failed).");
  }
  if (typeof updateProgress === "function") updateProgress(100, `Imported ${added} PNG${added===1?"":"s"}`);
  if (typeof endProgress === "function") setTimeout(endProgress, 250);

}

document.getElementById("addBtn").addEventListener("click", async ()=>{
  imageLoadToken++;
  let t = document.getElementById("promptInput").value.trim();
  const img = selectedImageDataUrl || "";
  const modelName = selectedModelName || "";

  let pulled = false;
  if (!t && selectedImageFile) {
    try {
      const extracted = await extractPromptFromFile(selectedImageFile);
      if (extracted) {
        t = extracted.trim();
        pulled = true;
      }
    } catch {}
  }

  if(!t && !img) return alert("Nothing to add");
  lib.push({ id:uid(), text:t, img, modelName });

  document.getElementById("promptInput").value="";
  selectedImageDataUrl = "";
  selectedImageFile = null;
  selectedModelName = "";
  hardResetImageInput();
  setDirty(true);

  render();
  updateStatus(pulled ? "Prompt pulled from image" : "Prompt added");
});
document.getElementById("openBtn").addEventListener("click", openLibrary);
document.getElementById("saveBtn").addEventListener("click", saveLibrary);
  document.getElementById("optimizeBtn").addEventListener("click", optimizeLibraryImagesToThumbnails);
document.getElementById("exportBtn").addEventListener("click", exportBackup);
document.getElementById("importBtn").addEventListener("click", importBackup);


// --- Tauri open-library / open-last-library wiring (auto, no clicks)
(async () => {
  try {
    const pending = await invoke("take_pending_open");
    if (pending?.type === "open-library" && pending.path) {
      await openLibraryFromPath(pending.path);
    } else if (pending?.type === "open-last-library") {
      await openLastLibrary();
    }
  } catch {}

  await listen("open-library", async (event) => {
    if (event.payload) await openLibraryFromPath(event.payload);
  });

  await listen("open-last-library", async () => {
    await openLastLibrary();
  });
})();

// --- Auto-save on close (no prompts, no blocking)
window.removeEventListener("beforeunload", () => {});
window.addEventListener("beforeunload", () => {
  if (!dirty) return;
  try { saveLibrary(); } catch (err) { console.warn("autosave failed", err); }
});

render();
updateStatus("Ready");



// Disable right-click everywhere EXCEPT the prompt input box
document.addEventListener(
  "contextmenu",
  (e) => {
    const promptInput = document.getElementById("promptInput");

    // Allow right-click inside the prompt textarea only
    if (promptInput && promptInput.contains(e.target)) {
      return; // allow default context menu
    }

    // Prevent right-click elsewhere
    e.preventDefault();
  },
  { capture: true }
);













// ---------------------
// Rendering + actions
// ---------------------
function escapeHtml(s){
  return String(s||"")
    .replaceAll("&","&amp;")
    .replaceAll("<","&lt;")
    .replaceAll(">","&gt;")
    .replaceAll('"',"&quot;")
    .replaceAll("'","&#039;");
}

function render(){
  updateOptimizeButtonVisibility();

  const list = document.getElementById("list");
  list.innerHTML = "";

  // Update sticky status count based on last saved/loaded
  updateStatus("Ready");

  for(const p of lib.slice().reverse()){
    const card = document.createElement("div");
    card.className = "card";

        card.style.border = "1px solid #ffffff";
    card.style.boxSizing = "border-box";

    const left = document.createElement("div");

    const header = document.createElement("div");
    header.className = "card-header";

    const copy = document.createElement("button");
    copy.className = "copybtn";
    copy.textContent = "Copy prompt";
    copy.addEventListener("click", async (e)=>{
      e.stopPropagation();
      const ok = await copyPromptToClipboard(p);
      updateStatus(ok ? "Copied prompt" : "Copy failed");
    });

    const pillrow = document.createElement("div");
    pillrow.className = "pillrow";

    const gen = document.createElement("div");
    gen.className = "pill";
    const combosCount = combos(p.text);
    gen.textContent = `Will Generate ${combosCount} Image${combosCount===1?"":"s"}`;
    pillrow.appendChild(gen);

    if(p.modelName){
      const model = document.createElement("div");
      model.className = "pill";
      model.textContent = p.modelName;
      pillrow.appendChild(model);
    }

    const del = document.createElement("button");
    del.className = "delbtn";
    del.textContent = "Delete";
    del.addEventListener("click", async (e)=>{
      e.stopPropagation();

      // Confirm before deleting
      const ok = await confirm("Delete this prompt?", {
        title: "Confirm delete",
        kind: "warning"
      });
      if(!ok) return;

      const idx = lib.findIndex(x=>x.id===p.id);
      if(idx>=0){
        lib.splice(idx,1);
        setDirty(true);
        render();
        updateStatus("Deleted");
      }
    });

    header.appendChild(copy);
    header.appendChild(pillrow);
    header.appendChild(del);

    const prompt = document.createElement("div");
    prompt.className = "prompt";
    prompt.textContent = p.text || "";

    left.appendChild(header);
    left.appendChild(prompt);

    const right = document.createElement("div");
    right.className = "rightpane";
    right.appendChild(del);
    if(p.img){
      const img = document.createElement("img");
      img.className = "thumb";
      img.src = p.img;
      right.appendChild(img);
    }

    card.appendChild(left);
    card.appendChild(right);

    list.appendChild(card);
  }
}

// ---------------------
// Image optimize utility
// ---------------------
async function optimizeLibraryImagesToThumbnails(){
  // Converts any embedded PNG data URLs to 512px JPEG data URLs
  // so the library file stays smaller and faster.
  const ok = await confirm("Optimize: convert embedded PNGs to 512px JPEG thumbnails? This changes stored images (not prompts).");
  if(!ok) return;

  let changed = 0;

  for(let i=0;i<lib.length;i++){
    const p = lib[i];
    if(typeof p.img === "string" && p.img.startsWith("data:image/png")){
      try{
        const blob = await (await fetch(p.img)).blob();
        const jpg = await imgToJpg(blob);
        if(jpg){
          p.img = jpg;
          changed++;
        }
      }catch{}
    }
  }

  if(changed){
    setDirty(true);
    render();
    updateStatus(`Optimized ${changed} image(s)`);
  }else{
    updateStatus("No PNGs to optimize");
  }
}
