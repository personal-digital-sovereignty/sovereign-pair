use tauri::{menu::{Menu, MenuItem}, tray::TrayIconBuilder, Manager};
#[cfg(target_os = "linux")]
use fs_extra::dir::{copy, CopyOptions};

#[tauri::command]
async fn install_desktop_widgets(#[allow(unused_variables)] app: tauri::AppHandle) -> Result<String, String> {
    #[cfg(target_os = "linux")]
    {
        let resource_dir = app.path().resource_dir().map_err(|_| "Falha ao obter pasta de recursos")?;
        let widget_src = resource_dir.join("infra/plasma-widget");
        
        if !widget_src.exists() {
            return Err("Widget fonte não encontrado no Bundle Cíbrido".to_string());
        }

        let local_data = app.path().local_data_dir().map_err(|_| "Falha ao obter ~/.local/share")?;
        let plasmoids_dir = local_data.join("plasma/plasmoids");
        
        std::fs::create_dir_all(&plasmoids_dir).map_err(|e| e.to_string())?;

        let target_dir = plasmoids_dir.join("com.sovereign.pair");
        if target_dir.exists() {
            std::fs::remove_dir_all(&target_dir).map_err(|e| e.to_string())?;
        }

        let mut options = CopyOptions::new();
        options.copy_inside = true;
        
        // Copy the uncompressed widget folder
        copy(&widget_src, &plasmoids_dir, &options).map_err(|e| e.to_string())?;
        
        // Rename to the official namespace
        let copied_name = plasmoids_dir.join("plasma-widget");
        if copied_name.exists() {
            std::fs::rename(&copied_name, &target_dir).map_err(|e| e.to_string())?;
        }

        // Notify KDE Plasma to reload/install the plasmoid
        let _ = std::process::Command::new("kpackagetool6")
            .arg("-t")
            .arg("Plasma/Applet")
            .arg("-u")
            .arg(&target_dir)
            .status();

        Ok("Extensão Plasma (KDE) Cíbrida implantada no Local User com sucesso!".to_string())
    }
    
    #[cfg(not(target_os = "linux"))]
    {
        Ok("Nenhuma extensão nativa (KDE/Gnome) se aplica a este S.O.".to_string())
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .plugin(tauri_plugin_fs::init())
    .plugin(tauri_plugin_shell::init())
    .plugin(tauri_plugin_os::init())
    .plugin(tauri_plugin_dialog::init())
    .setup(|app| {
      let quit_i = MenuItem::with_id(app, "quit", "Sair do Cíbrido", true, None::<&str>)?;
      let show_i = MenuItem::with_id(app, "show", "Abrir Painel", true, None::<&str>)?;
      let menu = Menu::with_items(app, &[&show_i, &quit_i])?;

      let _tray = TrayIconBuilder::new()
        .icon(app.default_window_icon().unwrap().clone())
        .menu(&menu)
        .on_menu_event(|app, event| match event.id.as_ref() {
            "quit" => app.exit(0),
            "show" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
            _ => {}
        })
        .build(app)?;

      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      Ok(())
    })
    .on_window_event(|window, event| match event {
        tauri::WindowEvent::CloseRequested { api, .. } => {
            let _ = window.hide();
            api.prevent_close();
        }
        _ => {}
    })
    .invoke_handler(tauri::generate_handler![install_desktop_widgets])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
