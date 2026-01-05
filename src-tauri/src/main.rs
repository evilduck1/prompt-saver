#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Emitter;

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
