#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

fn main() {
  tauri::Builder::default()
    .plugin(tauri_plugin_dialog::init())
    .plugin(tauri_plugin_fs::init())
    .setup(|app| {
      // Collect file paths passed on launch (file association / open-with)
      let paths: Vec<String> = std::env::args()
        .skip(1)
        .filter(|arg| arg.ends_with(".promptsaver"))
        .collect();

      let handle = app.handle();

      if let Some(path) = paths.first().cloned() {
        // macOS may pass multiple files — open the first
        let _ = handle.emit_all("open-library", path);
      } else {
        // No file passed → frontend auto-opens last library
        let _ = handle.emit_all("open-last-library", ());
      }

      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
