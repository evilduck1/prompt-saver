#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{Manager};

fn main() {
  tauri::Builder::default()
    .plugin(tauri_plugin_dialog::init())
    .plugin(tauri_plugin_fs::init())
    .setup(|app| {
      // Collect file paths passed on launch (file association / open-with)
      let mut paths: Vec<String> = std::env::args()
        .skip(1)
        .filter(|arg| arg.ends_with(".promptsaver"))
        .collect();

      // If no file was passed, try to load last opened library
      if paths.is_empty() {
        if let Some(path) = app
          .config()
          .tauri
          .unwrap_or_default()
          .bundle
          .unwrap_or_default()
          .identifier
          .as_ref()
        {
          // frontend will decide what to do if empty
          let _ = app.emit_all("open-last-library", ());
        }
      } else {
        // Emit first file path (macOS may pass multiple)
        let _ = app.emit_all("open-library", paths.remove(0));
      }

      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
