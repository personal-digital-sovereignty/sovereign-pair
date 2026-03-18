// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn open_studio_mode(app: tauri::AppHandle, port: u16) {
    let url = format!("http://127.0.0.1:{}", port);
    
    // Foca se já existir a janela
    if let Some(win) = tauri::Manager::get_webview_window(&app, "studio") {
        let _ = win.set_focus();
        return;
    }

    let _window = tauri::WebviewWindowBuilder::new(
        &app,
        "studio",
        tauri::WebviewUrl::External(url.parse().unwrap())
    )
    .title("Sovereign Pair Studio")
    .inner_size(1400.0, 900.0)
    .center()
    .build();
}

use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    Manager,
};
use tauri_plugin_shell::ShellExt;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            // SPONTANEOUS HUB MODE (As requested by User)
            // Starts the Rust API Sidecar in background listening on 0.0.0.0.
            let sidecar_command = app.shell().sidecar("sovereign-axum").unwrap()
                .args(["--host", "0.0.0.0"]);
            
            let (mut rx, _child) = sidecar_command.spawn().expect("Falha ao iniciar o Motor Sovereign Core (Sidecar)");
            
            // Spawn an async task to monitor the Sidecar's stdout/stderr
            tauri::async_runtime::spawn(async move {
                while let Some(event) = rx.recv().await {
                    match event {
                        tauri_plugin_shell::process::CommandEvent::Stdout(line) => {
                            println!("[API SIDECAR]: {}", String::from_utf8_lossy(&line));
                        }
                        tauri_plugin_shell::process::CommandEvent::Stderr(error) => {
                            eprintln!("[API SIDECAR ERROR]: {}", String::from_utf8_lossy(&error));
                        }
                        tauri_plugin_shell::process::CommandEvent::Terminated(payload) => {
                            eprintln!("[API SIDECAR EXITED]: Code {:?}", payload.code);
                        }
                        _ => {}
                    }
                }
            });
            let quit_i = MenuItem::with_id(app, "quit", "Encerrar Sovereign Pair", true, None::<&str>)?;
            let show_i = MenuItem::with_id(app, "show", "Exibir Spotlight", true, None::<&str>)?;
            let hide_i = MenuItem::with_id(app, "hide", "Ocultar Spotlight", true, None::<&str>)?;
            
            let menu = Menu::with_items(app, &[&show_i, &hide_i, &quit_i])?;

            let _tray = TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .menu(&menu)
                .show_menu_on_left_click(false)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "quit" => {
                        std::process::exit(0);
                    }
                    "show" => {
                        if let Some(window) = app.get_webview_window("main") {
                            window.show().unwrap();
                            window.set_focus().unwrap();
                        }
                    }
                    "hide" => {
                        if let Some(window) = app.get_webview_window("main") {
                            window.hide().unwrap();
                        }
                    }
                    _ => {
                        println!("menu item {:?} not handled", event.id);
                    }
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        let app = tray.app_handle();
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    } else if let TrayIconEvent::Click {
                        button: MouseButton::Right,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        #[cfg(target_os = "macos")]
                        {
                            let app = tray.app_handle();
                            if let Some(window) = app.get_webview_window("main") {
                                let _ = window.show();
                                let _ = window.set_focus();
                            }
                        }
                    }
                })
                .build(app)?;

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![greet, open_studio_mode])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
