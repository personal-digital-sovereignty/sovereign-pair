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

#[tauri::command]
async fn check_ollama_engine() -> Result<String, String> {
    // Fase 42: Bypassing WebView CORS for Ollama Detection via Rust Native TCP Socket
    match std::net::TcpStream::connect("127.0.0.1:11434") {
        Ok(_) => Ok("Motor Ollama detectado na Porta 11434 com sucesso!".to_string()),
        Err(e) => Err(format!("Ollama daemon offline: {}", e)),
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
      use tauri_plugin_shell::ShellExt;
      use tauri_plugin_shell::process::CommandEvent;

      // Fase 41: Sovereign Core Sidecar Spawning
      match app.shell().sidecar("sovereign-core") {
          Ok(sidecar_command) => {
              match sidecar_command.spawn() {
                  Ok((mut rx, _child)) => {
                      tauri::async_runtime::spawn(async move {
                          while let Some(event) = rx.recv().await {
                              if let CommandEvent::Stdout(line) = event {
                                  println!("[Core] {}", String::from_utf8_lossy(&line));
                              } else if let CommandEvent::Stderr(line) = event {
                                  eprintln!("[Core Err] {}", String::from_utf8_lossy(&line));
                              }
                          }
                      });
                  },
                  Err(e) => eprintln!("❌ Falha Máxima ao invocar Sidecar: {}", e),
              }
          },
          Err(e) => eprintln!("❌ Binário sidecar 'sovereign-core' não econtrado no bundle Desktop: {}", e),
      }

      let quit_i = MenuItem::with_id(app, "quit", "Sair do Cíbrido", true, None::<&str>)?;
      let show_i = MenuItem::with_id(app, "show", "Abrir Painel Principal", true, None::<&str>)?;
      let spotlight_i = MenuItem::with_id(app, "spotlight", "Abrir Spotlight Chat", true, None::<&str>)?;
      let menu = Menu::with_items(app, &[&show_i, &spotlight_i, &quit_i])?;

      let tray_icon = tauri::image::Image::from_bytes(include_bytes!("../icons/tray-icon.png")).expect("Failed to load tray icon");

      let _tray = TrayIconBuilder::new()
        .icon(tray_icon)
        .icon_as_template(true)
        .menu(&menu)
        .on_menu_event(|app, event| match event.id.as_ref() {
            "quit" => app.exit(0),
            "show" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
            "spotlight" => {
                if let Some(window) = app.get_webview_window("spotlight") {
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
        tauri::WindowEvent::Focused(focused) => {
            // Hide spotlight window strictly when it loses focus (Raycast style)
            if !focused && window.label() == "spotlight" {
                let _ = window.hide();
            }
        }
        _ => {}
    })
    .invoke_handler(tauri::generate_handler![install_desktop_widgets, check_ollama_engine])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
