fn main() {
    let mut total_gb = 24.0;
    let mut used_gb = 0.8;
    let mut local_found = false;

    if let Ok(entries) = std::fs::read_dir("/sys/class/drm") {
        for entry in entries.flatten() {
            let dev_path = entry.path().join("device");
            if dev_path.join("mem_info_vram_total").exists() {
                if let Ok(total_str) = std::fs::read_to_string(dev_path.join("mem_info_vram_total")) {
                    if let Ok(total_bytes) = total_str.trim().parse::<u64>() {
                        total_gb = total_bytes as f64 / 1_073_741_824.0;
                        local_found = true;
                    }
                }
                if let Ok(used_str) = std::fs::read_to_string(dev_path.join("mem_info_vram_used")) {
                    if let Ok(used_bytes) = used_str.trim().parse::<u64>() {
                        used_gb = used_bytes as f64 / 1_073_741_824.0;
                    }
                }
                if local_found { break; }
            }
        }
    }
    println!("Found: {}, Total: {}, Used: {}", local_found, total_gb, used_gb);
}
