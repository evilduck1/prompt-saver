#!/usr/bin/env python3
import shutil, sys
from pathlib import Path

JS = Path("src/main.js")
CAP = Path("src-tauri/capabilities/default.json")

OLD_COPY = '''    copy.addEventListener("click", async (e)=>{
      e.stopPropagation();
      const ok = await copyPromptToClipboard(p);
      updateStatus(ok ? "Copied prompt" : "Copy failed");
    });'''

NEW_COPY = '''    copy.addEventListener("click", async (e)=>{
      e.stopPropagation();
      const ok = await copyPromptToClipboard(p);
      updateStatus(ok ? "Copied prompt" : "Copy failed");
      if(ok){
        clearTimeout(copy._flash);
        copy.textContent = "Copied";
        copy.classList.add("copied");
        copy._flash = setTimeout(()=>{
          copy.textContent = "Copy prompt";
          copy.classList.remove("copied");
        }, 1200);
      }
    });'''

OLD_CLOSE = '''window.removeEventListener("beforeunload", () => {});
window.addEventListener("beforeunload", () => {
  if (!dirty) return;
  try { saveLibrary(); } catch (err) { console.warn("autosave failed", err); }
});'''

NEW_CLOSE = '''const mainWindow = getCurrentWindow();
mainWindow.onCloseRequested(async (event) => {
  if (!dirty) return;
  event.preventDefault();
  const ok = await confirm("You have unsaved changes. Save before closing?", {
    title: "Unsaved changes",
    kind: "warning"
  });
  if (ok) {
    await saveLibrary();
    if (dirty) return;
  }
  await mainWindow.destroy();
});'''

PATCHES = [
    ('import { invoke } from "@tauri-apps/api/core";',
     'import { invoke } from "@tauri-apps/api/core";\nimport { getCurrentWindow } from "@tauri-apps/api/window";'),

    ('.rightpane{position:relative;display:flex;justify-content:center;align-items:center}',
     '.rightpane{position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:12px;padding-left:14px}'),

    ('''.delbtn{
  appearance:none;''',
     '''.delbtn{
  margin-left:10px;
  appearance:none;'''),

    ('.copybtn:hover{background:rgba(255,255,255,.09)}',
     '.copybtn:hover{background:rgba(255,255,255,.09)}\n.copybtn.copied{background:rgba(58,166,117,.30);border-color:#3aa675}'),

    (OLD_COPY, NEW_COPY),
    (OLD_CLOSE, NEW_CLOSE),
]

def main():
    src = JS.read_text(encoding="utf-8")
    cap = CAP.read_text(encoding="utf-8")
    bad = [f"anchor {i}: {src.count(a)}" for i, (a, _) in enumerate(PATCHES, 1) if src.count(a) != 1]
    if bad:
        print("Anchor problems:"); print("\n".join(bad)); sys.exit(1)
    print(f"All {len(PATCHES)} anchors matched.")
    for a, r in PATCHES:
        src = src.replace(a, r, 1)
    if '"core:window:allow-destroy"' not in cap:
        cap = cap.replace('    "core:window:default",',
                          '    "core:window:default",\n    "core:window:allow-destroy",\n    "core:window:allow-close",')
    shutil.copy2(JS, JS.with_suffix(".js.bak3"))
    JS.write_text(src, encoding="utf-8")
    CAP.write_text(cap, encoding="utf-8")
    print("Patched.")

main()
