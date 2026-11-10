#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

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
      import_library,
      read_library,
      write_library,
      delete_library,
      get_last_library_path,
      set_last_library_path
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
