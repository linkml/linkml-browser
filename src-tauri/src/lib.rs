use serde::Serialize;
use std::sync::Mutex;

#[derive(Default)]
struct RecentLists {
  projects: Vec<String>,
  evaluations: Vec<String>,
}

struct RecentState(Mutex<RecentLists>);

#[derive(Serialize, Clone)]
struct RecentPayload {
  kind: String,
  path: String,
}

fn truncate_label(value: &str, max_len: usize) -> String {
  if value.len() <= max_len {
    return value.to_string();
  }
  let tail_len = max_len.saturating_sub(4);
  let tail = value
    .chars()
    .rev()
    .take(tail_len)
    .collect::<String>()
    .chars()
    .rev()
    .collect::<String>();
  format!("…{}", tail)
}

fn recent_label(path: &str, max_len: usize) -> String {
  let trimmed = path.trim();
  if trimmed.is_empty() {
    return "Unknown".into();
  }
  let short = truncate_label(trimmed, max_len);
  short
}

#[cfg(desktop)]
fn build_recent_submenu<R: tauri::Runtime>(
  handle: &tauri::AppHandle<R>,
  title: &str,
  prefix: &str,
  items: &[String],
) -> tauri::Result<tauri::menu::Submenu<R>> {
  use tauri::menu::{MenuItem, SubmenuBuilder};
  let mut builder = SubmenuBuilder::new(handle, title);
  if items.is_empty() {
    let empty_item = MenuItem::with_id(handle, format!("{}empty", prefix), "None", false, None::<&str>)?;
    builder = builder.item(&empty_item);
  } else {
    for (idx, path) in items.iter().enumerate() {
      let label = recent_label(path, 60);
      builder = builder.text(format!("{}{}", prefix, idx), label);
    }
  }
  builder.build()
}

#[cfg(desktop)]
fn build_menu<R: tauri::Runtime>(
  handle: &tauri::AppHandle<R>,
  recents: &RecentLists,
) -> tauri::Result<tauri::menu::Menu<R>> {
  use tauri::menu::{MenuBuilder, MenuItem, SubmenuBuilder};
  let app_menu = SubmenuBuilder::new(handle, "MANTRA")
    .text("app_about", "About MANTRA")
    .separator()
    .text("app_quit", "Quit")
    .build()?;

  let recent_projects = build_recent_submenu(handle, "Open Recent Project", "recent_project_", &recents.projects)?;
  let recent_evaluations =
    build_recent_submenu(handle, "Open Recent Evaluations", "recent_evaluation_", &recents.evaluations)?;

  let open_evaluations = MenuItem::with_id(
    handle,
    "file_open_annotations",
    "Open Evaluations…",
    true,
    Some("CmdOrCtrl+O"),
  )?;

  let file_menu = SubmenuBuilder::new(handle, "File")
    .text("file_open_dataset", "Open Project…")
    .text("file_open_github", "Open Project from GitHub…")
    .item(&recent_projects)
    .separator()
    .item(&open_evaluations)
    .item(&recent_evaluations)
    .text("file_save_annotations_as", "Save Evaluations As…")
    .build()?;

  let help_menu = SubmenuBuilder::new(handle, "Help")
    .text("help_docs", "Documentation")
    .text("help_about", "About MANTRA")
    .build()?;

  let edit_menu = SubmenuBuilder::new(handle, "Edit")
    .cut()
    .copy()
    .paste()
    .separator()
    .select_all()
    .build()?;

  let menu = MenuBuilder::new(handle)
    .item(&app_menu)
    .item(&file_menu)
    .item(&edit_menu)
    .item(&help_menu)
    .build()?;
  Ok(menu)
}

#[tauri::command]
fn set_recent_menus(
  app: tauri::AppHandle,
  state: tauri::State<RecentState>,
  projects: Vec<String>,
  evaluations: Vec<String>,
) -> Result<(), String> {
  let mut guard = state.0.lock().map_err(|_| "Recent menu lock poisoned".to_string())?;
  guard.projects = projects;
  guard.evaluations = evaluations;
  #[cfg(desktop)]
  {
    let menu = build_menu(&app, &guard).map_err(|e| e.to_string())?;
    app.set_menu(menu).map_err(|e| e.to_string())?;
  }
  Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  use tauri::{Emitter, Manager};

  tauri::Builder::default()
    .plugin(tauri_plugin_dialog::init())
    .plugin(tauri_plugin_fs::init())
    .plugin(tauri_plugin_shell::init())
    .manage(RecentState(Mutex::new(RecentLists::default())))
    .invoke_handler(tauri::generate_handler![set_recent_menus])
    .menu(|handle| build_menu(handle, &RecentLists::default()))
    .on_menu_event(|app, event| {
      let id = event.id().0.clone();
      if id == "app_quit" {
        app.exit(0);
        return;
      }

      if let Some(idx) = id.strip_prefix("recent_project_") {
        if idx != "empty" {
          if let Ok(index) = idx.parse::<usize>() {
            if let Some(state) = app.try_state::<RecentState>() {
              if let Ok(guard) = state.0.lock() {
                if let Some(path) = guard.projects.get(index) {
                  let _ = app.emit(
                    "menu-open-recent",
                    RecentPayload {
                      kind: "project".to_string(),
                      path: path.to_string(),
                    },
                  );
                  return;
                }
              }
            }
          }
        }
      }

      if let Some(idx) = id.strip_prefix("recent_evaluation_") {
        if idx != "empty" {
          if let Ok(index) = idx.parse::<usize>() {
            if let Some(state) = app.try_state::<RecentState>() {
              if let Ok(guard) = state.0.lock() {
                if let Some(path) = guard.evaluations.get(index) {
                  let _ = app.emit(
                    "menu-open-recent",
                    RecentPayload {
                      kind: "evaluation".to_string(),
                      path: path.to_string(),
                    },
                  );
                  return;
                }
              }
            }
          }
        }
      }

      let _ = app.emit("menu-action", id);
    })
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
