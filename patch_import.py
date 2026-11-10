#!/usr/bin/env python3
import shutil, sys
from pathlib import Path

JS = Path("src/main.js")
RS = Path("src-tauri/src/main.rs")

RS_CMD = '''#[tauri::command]
fn import_library(app: tauri::AppHandle, source_path: String) -> Result<String, String> {
  let raw = fs::read_to_string(&source_path).map_err(|e| e.to_string())?;
  let parsed: serde_json::Value = serde_json::from_str(&raw)
    .map_err(|_| "Not a valid library file".to_string())?;
  let dir = libs_dir(&app)?;
  let stem = PathBuf::from(&source_path)
    .file_stem().and_then(|s| s.to_str()).unwrap_or("library").to_string();
  let base = sanitize(&stem);
  let mut p = dir.join(format!("{base}.json"));
  let mut n = 1;
  while p.exists() {
    p = dir.join(format!("{base}-{n}.json"));
    n += 1;
  }
  let pretty = serde_json::to_string_pretty(&parsed).map_err(|e| e.to_string())?;
  fs::write(&p, pretty).map_err(|e| e.to_string())?;
  Ok(p.to_string_lossy().to_string())
}

'''

JS_FN = '''async function importLibrary(){
  try{
    if(dirty) await saveLibrary();
    const fp = await open({
      multiple:false,
      filters:[{name:"JSON", extensions:["json"]}]
    });
    if(!fp) return;
    const dest = await invoke("import_library", { sourcePath: fp });
    await openLibraryFromPath(dest);
    updateStatus("Library imported");
  }catch(e){
    console.error(e);
    alert("Failed to import library");
  }
}

'''

PATCHES = [
    ('<button id="newLibBtn" type="button">New Library</button>',
     '<button id="newLibBtn" type="button">New Library</button>\n    <button id="importLibBtn" type="button">Import Library</button>'),
    ('#[tauri::command]\nfn read_library(path: String) -> Result<String, String> {',
     RS_CMD + '#[tauri::command]\nfn read_library(path: String) -> Result<String, String> {'),
    ('      create_library,\n', '      create_library,\n      import_library,\n'),
    ('async function switchLibrary(path){', JS_FN + 'async function switchLibrary(path){'),
    ('document.getElementById("newLibBtn").addEventListener("click", newLibrary);',
     'document.getElementById("newLibBtn").addEventListener("click", newLibrary);\ndocument.getElementById("importLibBtn").addEventListener("click", importLibrary);'),
]

def main():
    src = JS.read_text(encoding="utf-8")
    rs = RS.read_text(encoding="utf-8")
    bad = []
    for i, (a, _) in enumerate(PATCHES, 1):
        target = rs if i == 2 or i == 3 else src
        if target.count(a) != 1:
            bad.append(f"anchor {i}: {target.count(a)}")
    if bad:
        print("Anchor problems:"); print("\n".join(bad)); sys.exit(1)
    print(f"All {len(PATCHES)} anchors matched.")
    for i, (a, r) in enumerate(PATCHES, 1):
        if i in (2, 3):
            rs = rs.replace(a, r, 1)
        else:
            src = src.replace(a, r, 1)
    shutil.copy2(JS, JS.with_suffix(".js.bak2"))
    shutil.copy2(RS, RS.with_suffix(".rs.bak2"))
    JS.write_text(src, encoding="utf-8")
    RS.write_text(rs, encoding="utf-8")
    print("Patched.")

main()
