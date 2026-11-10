#!/usr/bin/env python3
import shutil, sys
from pathlib import Path

JS = Path("src/main.js")
RS = Path("src-tauri/src/main.rs")

MAIN_RS = r'''#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::Serialize;
use std::fs;
use std::path::PathBuf;
use tauri::{Emitter, Manager};
use walkdir::WalkDir;

#[derive(Serialize)]
struct LibraryEntry { name: String, path: String, modified: u64 }

fn libs_dir(app: &tauri::AppHandle) -> Result<PathBuf, String> {
  let dir = app.path().app_data_dir().map_err(|e| e.to_string())?.join("libraries");
  fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
  Ok(dir)
}

fn sanitize(name: &str) -> String {
  let s: String = name.chars()
    .map(|c| if c.is_alphanumeric() || c == '-' || c == '_' || c == ' ' { c } else { '_' })
    .collect();
  let t = s.trim().trim_matches('.').to_string();
  if t.is_empty() { "library".into() } else { t }
}

#[tauri::command]
fn collect_pngs_from_folder(folder_path: String) -> Result<Vec<String>, String> {
  let mut pngs: Vec<String> = Vec::new();
  for entry in WalkDir::new(folder_path).follow_links(false).into_iter().filter_map(|e| e.ok()) {
    let path = entry.path();
    if path.is_file() {
      if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
        if ext.eq_ignore_ascii_case("png") {
          pngs.push(path.to_string_lossy().to_string());
        }
      }
    }
  }
  Ok(pngs)
}

#[tauri::command]
fn list_libraries(app: tauri::AppHandle) -> Result<Vec<LibraryEntry>, String> {
  let dir = libs_dir(&app)?;
  let mut out = Vec::new();
  for entry in fs::read_dir(&dir).map_err(|e| e.to_string())? {
    let entry = match entry { Ok(v) => v, Err(_) => continue };
    let p = entry.path();
    let is_json = p.extension().and_then(|x| x.to_str())
      .map(|x| x.eq_ignore_ascii_case("json")).unwrap_or(false);
    if !is_json { continue; }
    let name = p.file_stem().and_then(|x| x.to_str()).unwrap_or("library").to_string();
    let modified = fs::metadata(&p).and_then(|m| m.modified()).ok()
      .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
      .map(|d| d.as_millis() as u64).unwrap_or(0);
    out.push(LibraryEntry { name, path: p.to_string_lossy().to_string(), modified });
  }
  out.sort_by(|a, b| b.modified.cmp(&a.modified));
  Ok(out)
}

#[tauri::command]
fn create_library(app: tauri::AppHandle, name: String) -> Result<String, String> {
  let dir = libs_dir(&app)?;
  let base = sanitize(&name);
  let mut p = dir.join(format!("{base}.json"));
  let mut n = 1;
  while p.exists() {
    p = dir.join(format!("{base}-{n}.json"));
    n += 1;
  }
  fs::write(&p, "{\n  \"Prompts\": []\n}\n").map_err(|e| e.to_string())?;
  Ok(p.to_string_lossy().to_string())
}

#[tauri::command]
fn read_library(path: String) -> Result<String, String> {
  fs::read_to_string(&path).map_err(|e| e.to_string())
}

#[tauri::command]
fn write_library(path: String, contents: String) -> Result<(), String> {
  let p = PathBuf::from(&path);
  if p.exists() {
    let mut bak = p.clone().into_os_string();
    bak.push(".bak");
    let _ = fs::copy(&p, PathBuf::from(bak));
  }
  fs::write(&p, contents).map_err(|e| e.to_string())
}

#[tauri::command]
fn delete_library(path: String) -> Result<(), String> {
  fs::remove_file(&path).map_err(|e| e.to_string())
}

fn settings_path(app: &tauri::AppHandle) -> Result<PathBuf, String> {
  let dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
  fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
  Ok(dir.join("last_library.txt"))
}

#[tauri::command]
fn get_last_library_path(app: tauri::AppHandle) -> Result<Option<String>, String> {
  let p = settings_path(&app)?;
  Ok(fs::read_to_string(p).ok().map(|s| s.trim().to_string()).filter(|s| !s.is_empty()))
}

#[tauri::command]
fn set_last_library_path(app: tauri::AppHandle, path: String) -> Result<(), String> {
  let p = settings_path(&app)?;
  fs::write(p, path).map_err(|e| e.to_string())
}

fn main() {
  tauri::Builder::default()
    .plugin(tauri_plugin_dialog::init())
    .plugin(tauri_plugin_fs::init())
    .invoke_handler(tauri::generate_handler![
      collect_pngs_from_folder,
      list_libraries,
      create_library,
      read_library,
      write_library,
      delete_library,
      get_last_library_path,
      set_last_library
    ])
    .setup(|app| {
      let paths: Vec<String> = std::env::args().skip(1)
        .filter(|arg| arg.ends_with(".promptsaver"))
        .collect();
      let handle = app.handle();
      if let Some(path) = paths.first().cloned() {
        let _ = handle.emit("open-library", path);
      }
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
'''

CONTROLS = '''  <div class="controls">
    <h2>Library</h2>
    <select id="libSelect" title="Switch library"></select>
    <button id="newLibBtn" type="button">New Library</button>
    <button id="exportBtn" type="button">Export Backup</button>
    <button id="importBtn" type="button">Import Backup</button>
    <button id="saveBtn" type="button">Save</button>
    <button id="optimizeBtn" type="button" style="display:none" title="Convert embedded PNGs to 512px JPEG thumbnails">Optimize Images</button>
  </div>'''

MODAL = '''  <div id="list" class="list"></div>
</div>
  </div>
</div>

<div id="nameModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.65);z-index:20000;align-items:center;justify-content:center">
  <div style="background:#141414;border:1px solid #444;border-radius:14px;padding:20px;width:360px">
    <div class="small" style="margin-bottom:8px">New library name</div>
    <input id="nameInput" style="width:100%;padding:10px;border-radius:10px;border:1px solid #555;background:#0d0d0d;color:#eee" />
    <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:14px">
      <button id="nameCancel" type="button">Cancel</button>
      <button id="nameOk" type="button">Create</button>
    </div>
  </div>
</div>
`;'''

NEW_OPEN = r'''async function openLibraryFromPath(fp){
  if(typeof startProgress==="function") startProgress("Loading library…");
  if(typeof updateProgress==="function") updateProgress(5, "Opening…");
  try{
    const txt = await invoke("read_library", { path: fp });
    if(typeof updateProgress==="function") updateProgress(35, "Reading file…");
    const obj = JSON.parse(txt);
    if(typeof updateProgress==="function") updateProgress(60, "Parsing library…");
    lib = parseLibraryJson(obj);
    if(typeof updateProgress==="function") updateProgress(80, "Building view…");
    libraryMeta = obj && typeof obj === "object" && !Array.isArray(obj) ? obj : {};
    libraryLoaded = true;
    activePath = fp;
    const parts = String(fp).split(/[\\/]/);
    activeName = parts[parts.length - 1] || "Library";
    setDirty(false);
    savedCount = lib.length;
    render();
    if(typeof updateProgress==="function") updateProgress(100, "Done");
    if(typeof endProgress==="function") setTimeout(endProgress, 250);
    updateOptimizeButtonVisibility();
    updateStatus("Library loaded");
    try { await invoke("set_last_library_path", { path: fp }); } catch {}
    refreshLibraryList(fp);
  }catch(e){
    if(typeof endProgress==="function") endProgress();
    console.error(e);
    alert("Failed to open library");
  }
}

async function refreshLibraryList(selectPath){
  const sel = document.getElementById("libSelect");
  if(!sel) return;
  try{
    const list = await invoke("list_libraries");
    sel.innerHTML = "";
    for(const item of list){
      const o = document.createElement("option");
      o.value = item.path;
      o.textContent = item.name;
      if(item.path === (selectPath || activePath)) o.selected = true;
      sel.appendChild(o);
    }
  }catch(e){ console.error(e); }
}

function askName(def="Library"){
  return new Promise(resolve=>{
    const m = document.getElementById("nameModal");
    const i = document.getElementById("nameInput");
    if(!m || !i) return resolve(def);
    i.value = def;
    m.style.display = "flex";
    i.focus(); i.select();
    const finish = v => {
      m.style.display = "none";
      document.getElementById("nameOk").removeEventListener("click", ok);
      document.getElementById("nameCancel").removeEventListener("click", cancel);
      i.removeEventListener("keydown", key);
      resolve(v);
    };
    const ok = () => finish(i.value.trim() || "Library");
    const cancel = () => finish(null);
    const key = e => { if(e.key === "Enter") ok(); if(e.key === "Escape") cancel(); };
    document.getElementById("nameOk").addEventListener("click", ok);
    document.getElementById("nameCancel").addEventListener("click", cancel);
    i.addEventListener("keydown", key);
  });
}

async function newLibrary(){
  if(dirty) await saveLibrary();
  const name = await askName("Library");
  if(!name) return;
  try{
    const p = await invoke("create_library", { name });
    await openLibraryFromPath(p);
  }catch(e){
    console.error(e);
    alert("Failed to create library");
  }
}

async function switchLibrary(path){
  if(!path || path === activePath) return;
  if(dirty) await saveLibrary();
  await openLibraryFromPath(path);
}'''

NEW_SAVE = r'''async function saveLibrary(){
  try{
    let fp = activePath;
    if(!fp){
      fp = await invoke("create_library", { name: "Library" });
      activePath = fp;
      const parts = String(fp).split(/[\\/]/);
      activeName = parts[parts.length - 1] || "Library";
    }
    const payload = { ...libraryMeta, Prompts: lib };
    await invoke("write_library", { path: fp, contents: JSON.stringify(payload, null, 2) });
    setDirty(false);
    savedCount = lib.length;
    updateOptimizeButtonVisibility();
    updateStatus("Library saved");
    try { await invoke("set_last_library_path", { path: fp }); } catch {}
    refreshLibraryList(fp);
  }catch(e){
    console.error(e);
    alert("Failed to save library");
  }
}'''

NEW_LAST = r'''async function openLastLibrary(){
  try{
    const last = await invoke("get_last_library_path");
    if(last) return await openLibraryFromPath(last);
  }catch{}
  try{
    const list = await invoke("list_libraries");
    if(list.length) return await openLibraryFromPath(list[0].path);
    const p = await invoke("create_library", { name: "Library" });
    await openLibraryFromPath(p);
  }catch(e){ console.error(e); }
}'''

NEW_BOOT = '''(async () => {
  await listen("open-library", async (event) => {
    if (event.payload) await openLibraryFromPath(event.payload);
  });

  await listen("open-last-library", async () => {
    await openLastLibrary();
  });

  await openLastLibrary();
})();'''

OLD_OPEN = r'''async function openLibraryFromPath(fp){
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
}'''

OLD_SAVE = r'''async function saveLibrary(){
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
}'''

OLD_LAST = r'''async function openLastLibrary(){
  try{
    const last = await invoke("get_last_library_path");
    if(last) await openLibraryFromPath(last);
  }catch{}
}'''

OLD_BOOT = '''(async () => {
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
})();'''

OLD_OPENBTN = 'document.getElementById("openBtn").addEventListener("click", openLibrary);'
NEW_OPENBTN = '''document.getElementById("libSelect").addEventListener("change", (e)=> switchLibrary(e.target.value));
document.getElementById("newLibBtn").addEventListener("click", newLibrary);'''

PATCHES = [
    ('''  <div class="controls">
    <h2>Library</h2>
    <button id="exportBtn" type="button">Export Backup</button>
    <button id="importBtn" type="button">Import Backup</button>
    <button id="openBtn" type="button">Open Library</button>
    <button id="saveBtn" type="button">Save Library</button>
    <button id="optimizeBtn" type="button" style="display:none" title="Convert embedded PNGs to 512px JPEG thumbnails">Optimize Images</button>
  </div>''', CONTROLS),
    ('.controls{display:flex;gap:10px;flex-wrap:wrap;justify-self:end;align-items:center}',
     '.controls{display:flex;gap:10px;flex-wrap:wrap;justify-self:end;align-items:center}\n#libSelect{padding:10px 14px;border-radius:14px;border:1px solid var(--ui-muted);background:#141414;color:var(--text);max-width:220px}'),
    ('''  <div id="list" class="list"></div>
</div>
  </div>
</div>
`;''', MODAL),
    (OLD_OPEN, NEW_OPEN),
    (OLD_SAVE, NEW_SAVE),
    (OLD_LAST, NEW_LAST),
    (OLD_BOOT, NEW_BOOT),
    (OLD_OPENBTN, NEW_OPENBTN),
]

def main():
    src = JS.read_text(encoding="utf-8")
    bad = [f"anchor {i}: {src.count(a)}" for i, (a, _) in enumerate(PATCHES, 1) if src.count(a) != 1]
    if bad:
        print("Anchor problems:"); print("\n".join(bad)); sys.exit(1)
    print(f"All {len(PATCHES)} anchors matched.")
    out = src
    for a, r in PATCHES:
        out = out.replace(a, r, 1)
    shutil.copy2(JS, JS.with_suffix(".js.bak"))
    shutil.copy2(RS, RS.with_suffix(".rs.bak"))
    JS.write_text(out, encoding="utf-8")
    RS.write_text(MAIN_RS, encoding="utf-8")
    print("Patched src/main.js and src-tauri/src/main.rs")

main()
