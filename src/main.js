let imageLoadToken = 0;
import { open, save } from "@tauri-apps/plugin-dialog";
import { readTextFile, writeTextFile } from "@tauri-apps/plugin-fs";
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
}
*{box-sizing:border-box}
body{margin:24px;font-family:system-ui,Arial,sans-serif;background:var(--bg);color:var(--text)}
h1{margin:0;font-size:44px}
h2{margin:0;font-size:34px}
.small{font-size:12px;color:var(--muted)}
button{
  padding:10px 16px;border-radius:14px;border:1px solid var(--border2);
  background:var(--btnbg);color:var(--text);cursor:pointer
}
button:hover{background:var(--btnhover)}
button:disabled{opacity:.55;cursor:not-allowed}
.header{
  display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:16px;margin-bottom:18px
}
.header .right{justify-self:end;display:flex;gap:12px}
.inputs{
  display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:18px
}
textarea{
  width:100%;min-height:140px;padding:12px;border-radius:14px;
  border:1px solid var(--border2);background:rgba(255,255,255,.04);color:var(--text)
}
.thumb{width:100%;max-height:360px;object-fit:contain;border-radius:14px;border:1px solid var(--border);background:#0003}
.library-head{
  display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:14px;margin:14px 0
}
.badge{
  padding:8px 14px;border-radius:999px;border:1px solid var(--border2);
  font-size:34px;line-height:1
}
.controls{display:flex;gap:10px;flex-wrap:wrap;justify-self:end;align-items:center}
.list{display:grid;gap:16px}
.card{
  display:grid;grid-template-columns:2fr 1.2fr;gap:16px;
  padding:16px;border-radius:18px;background:var(--panel2);border:1px solid var(--border)
}
.card-header{display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:center}
.gen{font-weight:600;font-size:14px}
.prompt{
  white-space:pre-wrap;
  line-height:1.35;
  margin-top:8px;
  max-height: 20.5em;
  overflow: hidden;
}
@media(max-width:900px){
  .inputs,.card,.header,.library-head{grid-template-columns:1fr}
  .header .right,.controls{justify-self:start}
}
</style>

<div class="header">
  <h1>Prompt Saver</h1>
  <button id="addBtn" type="button">Add Prompt</button>
  <div class="right">
    <button id="clearAllBtn" type="button">Clear All</button>
  </div>
</div>

<div class="inputs">
  <div>
    <div class="small">prompt input box</div>
    <textarea id="promptInput" placeholder="Type your prompt..."></textarea>
  </div>
  <div>
    <div class="small">prompt image input box</div>
    <input id="imageInput" type="file" accept="image/*"/>
    <!-- input preview removed (keep only file picker) -->
  </div>
</div>

<div class="library-head">
  <div id="badge" class="badge" style="display:none">Unsaved Prompts</div>
  <div id="status" class="small"></div>
  <div class="controls">
    <h2>Library</h2>
    <button id="exportBtn" type="button">Export Backup (HTML)</button>
    <button id="importBtn" type="button">Import Backup (HTML)</button>
    <button id="openBtn" type="button">Open Library</button>
    <button id="saveBtn" type="button">Save Library</button>
  </div>
</div>

<div id="list" class="list"></div>
`;

const THUMB = 768;
const QUAL = 0.85;

let lib = [];
let dirty = false;
// Holds the currently-selected image for the *next* prompt (no input preview UI).
let selectedImageDataUrl = "";

let activePath = null;
let activeName = "No Library File Loaded";

function uid(){ return crypto.randomUUID?.() || ("id-"+Date.now()+"-"+Math.random().toString(16).slice(2)); }
function setDirty(v){ dirty=!!v; document.getElementById("badge").style.display = dirty ? "inline-flex" : "none"; }
function combos(t){
  let m,n=1,any=false,r=/\{([^}]+)\}/g;
  while((m=r.exec(t||""))){ any=true; n *= (m[1].split("|").map(s=>s.trim()).filter(Boolean).length || 1); }
  return any?n:1;
}
function updateStatus(prefix="Ready"){
  document.getElementById("status").textContent = `${prefix} • Prompts In Library: ${lib.length} • Library: ${activeName}`;
}
function normalizeItems(arr){
  if(!Array.isArray(arr)) return [];
  return arr.map(p=>{
    const text = (p?.text ?? p?.prompt ?? "").toString();
    const img  = (p?.img ?? p?.imageDataUrl ?? p?.image ?? "").toString();
    const id   = (p?.id ?? uid()).toString();
    return {id, text, img};
  }).filter(p => (p.text && p.text.trim()) || p.img);
}
function parseLibraryJson(obj){
  if(Array.isArray(obj)) return normalizeItems(obj);
  if(obj && Array.isArray(obj.Prompts)) return normalizeItems(obj.Prompts);
  if(obj && Array.isArray(obj.library)) return normalizeItems(obj.library);
  return [];
}
function buildPayload(){
  return {
    app: "Prompt Saver",
    version: "desktop-1.1.7",
    exportedAt: new Date().toISOString(),
    Prompts: lib.map(p => ({ id:p.id, prompt:p.text, imageDataUrl:p.img }))
  };
}

async function imgToJpg(file){
  const b = await createImageBitmap(file);
  const s = Math.min(1, THUMB / Math.max(b.width, b.height));
  const c = document.createElement("canvas");
  c.width = Math.max(1, Math.round(b.width*s));
  c.height = Math.max(1, Math.round(b.height*s));
  c.getContext("2d").drawImage(b,0,0,c.width,c.height);
  const blob = await new Promise(r=>c.toBlob(r,"image/jpeg",QUAL));
  return await new Promise(r=>{ const fr=new FileReader(); fr.onload=()=>r(fr.result); fr.readAsDataURL(blob); });
}

function render(){
  const list = document.getElementById("list");
  list.innerHTML = "";
  updateStatus("Ready");
  if(!lib.length) return;

  lib.slice().reverse().forEach(p=>{
    const c = document.createElement("div");
    c.className = "card";
    const n = combos(p.text);
    c.innerHTML = `
      <div>
        <div class="card-header">
          <button type="button" data-a="copy">Copy prompt</button>
          <div class="gen">Will Generate ${n} Image${n===1?"":"s"}</div>
          <button type="button" data-a="del">Delete</button>
        </div>
        <div class="prompt"></div>
      </div>
      <div>${p.img ? `<img class="thumb" src="${p.img}" alt=""/>` : `<div class="small">No image</div>`}</div>
    `;
    c.querySelector(".prompt").textContent = p.text || "";

    const delBtn = c.querySelector('[data-a="del"]');
    const copyBtn = c.querySelector('[data-a="copy"]');

    delBtn.addEventListener("click", (e)=>{
      e.preventDefault();
      e.stopPropagation();
      if(!confirm("Delete this prompt?")) return;
      lib = lib.filter(x=>x.id!==p.id);
      setDirty(true);
      render();
      updateStatus("Prompt deleted");
    });

    copyBtn.addEventListener("click", async (e)=>{
      e.preventDefault();
      e.stopPropagation();
      try{ await navigator.clipboard.writeText(p.text||""); }catch{}
      updateStatus("Copied prompt");
    });

    list.appendChild(c);
  });
}


async function openLibrary(){
  if(dirty && !confirm("Discard unsaved prompts?")) return;

  const selected = await open({
    multiple: false,
    filters: [{ name: "Prompt Saver Library", extensions: ["json"] }]
  });
  if(!selected) return;
  const path = Array.isArray(selected) ? selected[0] : selected;

  const text = await readTextFile(path);
  const obj = JSON.parse(text);

  lib = parseLibraryJson(obj);
  activePath = path;
  activeName = await basename(path);
  setDirty(false);

  render();
  updateStatus("Loaded Library");
}

async function saveLibrary(){
  try {
    const jsonText = JSON.stringify(buildPayload(), null, 2);

    if(activePath){
      await writeTextFile(activePath, jsonText);
      setDirty(false);
      updateStatus("Library saved");
      return;
    }

    const chosen = await save({
      defaultPath: "prompt-saver-library.json",
      filters: [{ name: "Prompt Saver Library", extensions: ["json"] }]
    });
    if(!chosen) return;

    activePath = chosen;
    activeName = await basename(chosen);

    await writeTextFile(activePath, jsonText);
    setDirty(false);
    
    updateStatus("Library saved");
  } catch (err) {
    console.error("Save failed:", err);
    alert("Save failed:\n\n" + (err?.message || err));
    updateStatus("Save failed");
  }
}

async function exportBackup(){
  const payload = buildPayload();
  const marker = `<!--PROMPT_SAVER_BACKUP:${btoa(unescape(encodeURIComponent(JSON.stringify(payload))))}-->`;
  const doc = `<!doctype html><html><head><meta charset="utf-8"/><title>Prompt Saver Backup</title></head><body><h1>Prompt Saver Backup</h1>${marker}</body></html>`;

  let defaultName = "prompt-saver-library.backup.html";
  let defaultFolder = null;

  if(activePath){
    const name = await basename(activePath);
    const ext = await extname(name);
    const base = ext ? name.slice(0, -ext.length) : name;
    defaultName = `${base}.backup.html`;
    defaultFolder = await dirname(activePath);
  }

  const defaultPath = defaultFolder ? await join(defaultFolder, defaultName) : defaultName;

  const chosen = await save({
    defaultPath,
    filters: [{ name: "Prompt Saver Backup", extensions: ["html"] }]
  });
  if(!chosen) return;

  await writeTextFile(chosen, doc);
  updateStatus("Exported backup (no state changed)");
}

async function importBackup(){
  const selected = await open({
    multiple:false,
    filters:[{ name:"Prompt Saver Backup", extensions:["html"] }]
  });
  if(!selected) return;

  const path = Array.isArray(selected) ? selected[0] : selected;
  const text = await readTextFile(path);
  const m = text.match(/<!--PROMPT_SAVER_BACKUP:([A-Za-z0-9+/=]+)-->/);
  if(!m) return alert("Invalid backup file.");

  const payload = JSON.parse(decodeURIComponent(escape(atob(m[1]))));
  const imported = parseLibraryJson(payload);

  const replace = confirm(`Found ${imported.length} prompts in backup.\n\nOK = Replace current prompts\nCancel = Merge`);
  if(replace){
    lib = imported;
  }else{
    const seen = new Set(lib.map(p=>p.text+"||"+p.img));
    for(const p of imported){
      const k = p.text+"||"+p.img;
      if(seen.has(k)) continue;
      lib.push({ id:uid(), text:p.text, img:p.img });
      seen.add(k);
    }
  }
  setDirty(true);

  render();
  updateStatus("Imported backup");
}

async function onImageChange(e) {
  const file = e.target.files?.[0];
  const myToken = ++imageLoadToken;
  if (!file) {
    selectedImageDataUrl = "";
    return;
  }

  // No preview: just read and store.
  const r = new FileReader();
  r.onload = () => {
    if (myToken !== imageLoadToken) return;
    selectedImageDataUrl = String(r.result || "");
  };
  r.readAsDataURL(file);
}
document.getElementById("imageInput").addEventListener("change", onImageChange);

function hardResetImageInput() {
  const oldInput = document.getElementById("imageInput");
  const newInput = oldInput.cloneNode(true);
  oldInput.replaceWith(newInput);
  newInput.addEventListener("change", onImageChange);
}
document.getElementById("addBtn").addEventListener("click", ()=>{
  imageLoadToken++;
  const t = document.getElementById("promptInput").value.trim();
  const img = selectedImageDataUrl || "";
  if(!t && !img) return alert("Nothing to add");
  lib.push({ id:uid(), text:t, img });
  document.getElementById("promptInput").value="";
  selectedImageDataUrl = "";
  hardResetImageInput();
  setDirty(true);

  render();
  updateStatus("Prompt added");
});
document.getElementById("clearAllBtn").addEventListener("click", ()=>{
  if(!lib.length || !confirm("Clear ALL prompts?")) return;
  lib=[];
  setDirty(true);

  render();
  updateStatus("Library cleared");
});

document.getElementById("openBtn").addEventListener("click", openLibrary);
document.getElementById("saveBtn").addEventListener("click", saveLibrary);
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

