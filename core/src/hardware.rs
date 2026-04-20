use ash::{vk, Entry};
use sysinfo::System;
use std::ffi::CStr;
use tracing::{info, warn};

pub struct HardwareTelemetry {
    pub total_ram_gb: f32,
    pub used_ram_gb: f32,
    pub total_vram_gb: f32,
    pub used_vram_gb: f32, // Note: Vulkan ash cannot natively read realtime generic heap *usage* easily without specific extensions like VK_EXT_memory_budget, we'll return 0.0 for usage if extension isn't loaded, but total is accurate.
    pub gpu_name: String,
}

/// Dynamically calculates safe Context Windows based on GPU VRAM availability, with fallback to System RAM.
pub fn calculate_safe_context_window(telemetry: &HardwareTelemetry) -> u64 {
    // Priority 1: VRAM drives context windows primarily for ML (unless CPU bound)
    let governing_memory = if telemetry.total_vram_gb > 0.0 {
        telemetry.total_vram_gb
    } else {
        telemetry.total_ram_gb
    };

    if governing_memory < 8.0 {
        4096 // Tight lock for low-end devices
    } else if governing_memory < 16.0 {
        8192 // Standard fallback for 8-15GB VRAM/RAM
    } else if governing_memory < 24.0 {
        12288 // Comfort zone for 16-24GB (typical developer setups)
    } else {
        16384 // Raw absolute power for 24GB+ (e.g. RTX 3090, 4090, or heavy Macs)
    }
}

pub fn capture_hardware_telemetry() -> HardwareTelemetry {
    let mut sys = System::new_all();
    sys.refresh_memory();
    let total_ram_gb = sys.total_memory() as f32 / 1024.0 / 1024.0 / 1024.0;
    let used_ram_gb = sys.used_memory() as f32 / 1024.0 / 1024.0 / 1024.0;

    let mut total_vram_gb = 0.0;
    let mut used_vram_gb = 0.0;
    let mut gpu_name = "N/A".to_string();

    // Try extracting via Vulkan
    unsafe {
        if let Ok(entry) = Entry::load() {
            let app_info = vk::ApplicationInfo::default().api_version(vk::make_api_version(0, 1, 0, 0));
            let create_info = vk::InstanceCreateInfo::default().application_info(&app_info);
            
            if let Ok(instance) = entry.create_instance(&create_info, None) {
                if let Ok(pdevices) = instance.enumerate_physical_devices() {
                    let mut max_vram = 0;
                    for &pdevice in pdevices.iter() {
                        let props = instance.get_physical_device_properties(pdevice);
                        let name_cstr = CStr::from_ptr(props.device_name.as_ptr());
                        let current_gpu_name = name_cstr.to_string_lossy().into_owned();
                        
                        let mem_props = instance.get_physical_device_memory_properties(pdevice);
                        let mut current_vram = 0;
                        for i in 0..mem_props.memory_heap_count {
                            let heap = mem_props.memory_heaps[i as usize];
                            if heap.flags.contains(vk::MemoryHeapFlags::DEVICE_LOCAL) {
                                current_vram += heap.size;
                            }
                        }
                        
                        // O Sovereign sempre assume a Placa de Vídeo mais robusta como Primary Target (Single-GPU bias)
                        if current_vram > max_vram {
                            max_vram = current_vram;
                            gpu_name = current_gpu_name;
                        }
                    }
                    total_vram_gb = max_vram as f32 / 1024.0 / 1024.0 / 1024.0;
                }
                instance.destroy_instance(None);
            } else {
                warn!("⚠️ [Hardware Configurator] Failed to initialize Vulkan Instance. VRAM will report 0.");
            }
        } else {
            warn!("⚠️ [Hardware Configurator] Vulkan Loader NOT FOUND on Host. Running deep fallback (CPU Bound).");
        }
    }

    HardwareTelemetry {
        total_ram_gb,
        used_ram_gb,
        total_vram_gb,
        used_vram_gb,
        gpu_name
    }
}
