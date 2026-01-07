#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Emitter;
use walkdir::WalkDir;

#[tauri::command]
fn collect_pngs_from_folder(folder_path: String) -> Result<Vec<String>, String> {
  let mut pngs: Vec<String> = Vec::new();

  for entry in WalkDir::new(folder_path)
    .follow_links(false)
    .into_iter()
    .filter_map(|e| e.ok())
  {
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

fn main() {
  tauri::Builder::default()
    .plugin(tauri_plugin_dialog::init())
    .plugin(tauri_plugin_fs::init())
    .invoke_handler(tauri::generate_handler![collect_pngs_from_folder])
    .setup(|app| {
      // Collect file paths passed on launch (file association / open-with)
      let paths: Vec<String> = std::env::args()
        .skip(1)
        .filter(|arg| arg.ends_with(".promptsaver"))
        .collect();

      let handle = app.handle();

      if let Some(path) = paths.first().cloned() {
        // Open library directly
        let _ = handle.emit("open-library", path);
      } else {
        // No file → frontend auto-opens last library
        let _ = handle.emit("open-last-library", ());
      }

      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
