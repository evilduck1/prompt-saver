#!/usr/bin/env python3
"""
patch_prompt_saver.py — adds steps / cfg / shift capture to src/main.js

Usage (from the repo root):
    python3 patch_prompt_saver.py --check     # verify anchors only
    python3 patch_prompt_saver.py             # apply
    git add -A && git commit -m "capture steps, cfg, shift" && git push
"""

import argparse
import shutil
import sys
from pathlib import Path

TARGET = Path("src/main.js")

HELPERS = '''function numOrNull(v){
  if(v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}
function strOrNull(v){
  if(v === null || v === undefined) return null;
  const s = String(v).trim();
  return s || null;
}

function findDenoiseNode(graph){
  const nodes = graph?.nodes || {};
  for(const key of Object.keys(nodes)){
    const t = String(nodes[key]?.type || "");
    if(t.endsWith("_denoise") || t === "denoise_latents") return nodes[key];
  }
  return null;
}

'''

NEW_NORMALIZE = '''function normalizeItems(arr){
  if(!Array.isArray(arr)) return [];
  return arr.map(p=>{
    const text = (p?.text ?? p?.prompt ?? "").toString();
    const img  = (p?.img ?? p?.imageDataUrl ?? p?.image ?? "").toString();
    const id   = (p?.id ?? uid()).toString();
    const modelName = (p?.modelName ?? p?.model ?? p?.model_name ?? "").toString();
    const params = {
      steps: numOrNull(p?.params?.steps),
      cfg:   numOrNull(p?.params?.cfg),
      shift: strOrNull(p?.params?.shift),
    };
    return {id, text, img, modelName, params};
  }).filter(p => (p.text && p.text.trim()) || p.img);
}
'''

EXTRACTOR = '''function extractParamsFromTextChunks(chunks){
  const out = {steps:null, cfg:null, shift:null};

  out.steps = numOrNull(chunks.steps ?? chunks.Steps);
  out.cfg   = numOrNull(chunks.cfg_scale ?? chunks.cfg ?? chunks["CFG scale"]);
  out.shift = strOrNull(chunks.shift ?? chunks.z_image_shift);

  if(chunks.invokeai_metadata){
    try{
      const m = JSON.parse(chunks.invokeai_metadata);
      out.steps ??= numOrNull(m.steps);
      out.cfg   ??= numOrNull(m.cfg_scale);
      out.shift ??= strOrNull(m.z_image_shift ?? m.shift);
    }catch{}
  }

  if(chunks.invokeai_graph){
    try{
      const dn = findDenoiseNode(JSON.parse(chunks.invokeai_graph));
      out.steps ??= numOrNull(dn?.steps);
      out.cfg   ??= numOrNull(dn?.guidance_scale);
      out.shift ??= strOrNull(dn?.shift);
    }catch{}
  }

  if(chunks.parameters){
    const t = String(chunks.parameters);
    const s = t.match(/Steps:\\s*(\\d+)/i);        if(s) out.steps ??= numOrNull(s[1]);
    const c = t.match(/CFG scale:\\s*([\\d.]+)/i); if(c) out.cfg   ??= numOrNull(c[1]);
    const h = t.match(/Shift:\\s*([^\\n,]+)/i);    if(h) out.shift ??= strOrNull(h[1]);
  }

  return out;
}

async function extractParamsFromFile(file){
  if(!file) return null;
  const isPng = (file.type === "image/png") || (file.name || "").toLowerCase().endsWith(".png");
  if(!isPng) return null;
  const chunks = await parsePngTextChunks(file);
  return extractParamsFromTextChunks(chunks);
}

'''

PILLS = '''
    const p2 = p.params || {};
    if(p2.steps != null){
      const el = document.createElement("div"); el.className = "pill";
      el.textContent = `Steps ${p2.steps}`; pillrow.appendChild(el);
    }
    if(p2.cfg != null){
      const el = document.createElement("div"); el.className = "pill";
      el.textContent = `CFG ${p2.cfg}`; pillrow.appendChild(el);
    }
    if(p2.shift){
      const el = document.createElement("div"); el.className = "pill";
      el.textContent = `Shift ${p2.shift}`; pillrow.appendChild(el);
    }'''

PATCHES = [
    # 1. normalizeItems + helpers
    ('''function normalizeItems(arr){
  if(!Array.isArray(arr)) return [];
  return arr.map(p=>{
    const text = (p?.text ?? p?.prompt ?? "").toString();
    const img  = (p?.img ?? p?.imageDataUrl ?? p?.image ?? "").toString();
    const id   = (p?.id ?? uid()).toString();
    const modelName = (p?.modelName ?? p?.model ?? p?.model_name ?? "").toString();
    return {id, text, img, modelName};
  }).filter(p => (p.text && p.text.trim()) || p.img);
}
''',
     HELPERS + NEW_NORMALIZE),

    # 2. extractor
    ('async function extractModelNameFromFile(file){', EXTRACTOR + 'async function extractModelNameFromFile(file){'),

    # 3. state var
    ('let selectedModelName = ""; // extracted from uploaded PNG metadata (best-effort)',
     'let selectedModelName = ""; // extracted from uploaded PNG metadata (best-effort)\nlet selectedImageParams = null;'),

    # 4. reset in onImageChange
    ('  selectedModelName = "";\n  if (!file) {',
     '  selectedModelName = "";\n  selectedImageParams = null;\n  if (!file) {'),

    # 5. promises in onImageChange
    ('''  const thumbPromise = imgToJpg(file).catch(() => "");
  const modelPromise = extractModelNameFromFile(file).catch(() => "");

  const [thumbDataUrl, modelName] = await Promise.all([thumbPromise, modelPromise]);''',
     '''  const thumbPromise  = imgToJpg(file).catch(() => "");
  const modelPromise  = extractModelNameFromFile(file).catch(() => "");
  const paramsPromise = extractParamsFromFile(file).catch(() => null);

  const [thumbDataUrl, modelName, params] = await Promise.all([thumbPromise, modelPromise, paramsPromise]);'''),

    # 6. store params after token check
    ('  if (myToken !== imageLoadToken) return;\n\n  selectedImageDataUrl = String(thumbDataUrl || "");',
     '  if (myToken !== imageLoadToken) return;\n\n  selectedImageParams = params || null;\n  selectedImageDataUrl = String(thumbDataUrl || "");'),

    # 7. push in addBtn
    ('  lib.push({ id:uid(), text:t, img, modelName });',
     '  lib.push({ id:uid(), text:t, img, modelName, params: selectedImageParams });'),

    # 8. reset after addBtn
    ('  selectedModelName = "";\n  hardResetImageInput();',
     '  selectedModelName = "";\n  selectedImageParams = null;\n  hardResetImageInput();'),

    # 9. batch promises
    ('''      const thumbPromise = imgToJpg(file).catch(() => "");
      const modelPromise = extractModelNameFromFile(file).catch(() => "");
      const promptPromise = extractPromptFromFile(file).catch(() => "");

      const [thumbDataUrl, modelName, extractedPrompt] =
        await Promise.all([thumbPromise, modelPromise, promptPromise]);''',
     '''      const thumbPromise  = imgToJpg(file).catch(() => "");
      const modelPromise  = extractModelNameFromFile(file).catch(() => "");
      const promptPromise = extractPromptFromFile(file).catch(() => "");
      const paramsPromise = extractParamsFromFile(file).catch(() => null);

      const [thumbDataUrl, modelName, extractedPrompt, params] =
        await Promise.all([thumbPromise, modelPromise, promptPromise, paramsPromise]);'''),

    # 10. batch push
    ('''      lib.push({
        id: uid(),
        text: String(extractedPrompt || "").trim(),
        img: String(thumbDataUrl || ""),
        modelName: String(modelName || "")
      });''',
     '''      lib.push({
        id: uid(),
        text: String(extractedPrompt || "").trim(),
        img: String(thumbDataUrl || ""),
        modelName: String(modelName || ""),
        params: params || null
      });'''),

    # 11. importBackup merge
    ('''    lib.push(...incoming.map(p => ({
      id: uid(),
      text: p.text || "",
      img: p.img || "",
      modelName: p.modelName || ""
    })));''',
     '''    lib.push(...incoming.map(p => ({
      id: uid(),
      text: p.text || "",
      img: p.img || "",
      modelName: p.modelName || "",
      params: p.params || null
    })));'''),

    # 12. render pills
    ('''    if(p.modelName){
      const model = document.createElement("div");
      model.className = "pill";
      model.textContent = p.modelName;
      pillrow.appendChild(model);
    }''',
     '''    if(p.modelName){
      const model = document.createElement("div");
      model.className = "pill";
      model.textContent = p.modelName;
      pillrow.appendChild(model);
    }''' + PILLS),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify anchors, write nothing")
    args = ap.parse_args()

    if not TARGET.exists():
        sys.exit(f"{TARGET} not found — run this from the repo root.")

    src = TARGET.read_text(encoding="utf-8")
    problems = []

    for i, (anchor, _) in enumerate(PATCHES, 1):
        n = src.count(anchor)
        if n != 1:
            problems.append(f"  patch {i}: anchor found {n} times (expected 1)")

    if problems:
        print("Anchor problems:")
        print("\n".join(problems))
        print("\nNothing written. The file may already be patched or has diverged.")
        sys.exit(1)

    print(f"All {len(PATCHES)} anchors matched exactly once.")
    if args.check:
        return

    out = src
    for anchor, replacement in PATCHES:
        out = out.replace(anchor, replacement, 1)

    shutil.copy2(TARGET, TARGET.with_suffix(".js.bak"))
    TARGET.write_text(out, encoding="utf-8")

    print(f"Patched {TARGET}")
    print(f"Backup at {TARGET.with_suffix('.js.bak')}")
    print("\nNext:")
    print("  npm run tauri build")
    print("  git add -A && git commit -m \"capture steps, cfg, shift\" && git push")


if __name__ == "__main__":
    main()