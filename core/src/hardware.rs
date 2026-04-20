use ash::{vk, Entry};
use sysinfo::System;
use std::ffi::CStr;
use std::sync::OnceLock;
use tracing::warn;

#[derive(Clone, Debug)]
pub struct HardwareTelemetry {
    pub total_ram_gb: f64,
    pub used_ram_gb: f64,
    pub total_vram_gb: f64,
    pub used_vram_gb: f64, 
    pub gpu_name: String,
}

static HARDWARE_TELEMETRY_CACHE: OnceLock<HardwareTelemetry> = OnceLock::new();

struct VkInstanceGuard(ash::Instance);
impl Drop for VkInstanceGuard {
    fn drop(&mut self) {
        unsafe { self.0.destroy_instance(None); }
    }
}

/// Dynamically calculates safe Context Windows based on GPU VRAM availability, with fallback to System RAM.
pub fn calculate_safe_context_window(telemetry: &HardwareTelemetry) -> u64 {
    let governing_memory = if telemetry.total_vram_gb > 0.0 {
        telemetry.total_vram_gb
    } else {
        telemetry.total_ram_gb
    };

    if governing_memory < 8.0 {
        4096 
    } else if governing_memory < 16.0 {
        8192 
    } else if governing_memory < 24.0 {
        12288 
    } else {
        16384 
    }
}

pub fn capture_hardware_telemetry() -> HardwareTelemetry {
    HARDWARE_TELEMETRY_CACHE.get_or_init(|| {
        let mut sys = System::new_all();
        sys.refresh_memory();
        let total_ram_gb = sys.total_memory() as f64 / 1024.0 / 1024.0 / 1024.0;
        let used_ram_gb = sys.used_memory() as f64 / 1024.0 / 1024.0 / 1024.0;

        let mut total_vram_gb = 0.0;
        let used_vram_gb = 0.0;
        let mut gpu_name = "N/A".to_string();

        unsafe {
            if let Ok(entry) = Entry::load() {
                let app_info = vk::ApplicationInfo::default().api_version(vk::make_api_version(0, 1, 0, 0));
                let create_info = vk::InstanceCreateInfo::default().application_info(&app_info);
                
                if let Ok(instance) = entry.create_instance(&create_info, None) {
                    let _guard = VkInstanceGuard(instance.clone()); // GAP-04 RAII Guard!
                    
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
                            
                            if current_vram > max_vram {
                                max_vram = current_vram;
                                gpu_name = current_gpu_name;
                            }
                        }
                        total_vram_gb = max_vram as f64 / 1024.0 / 1024.0 / 1024.0; // GAP-06 f64 Precision
                    }
                } else {
                    warn!("⚠️ [Hardware] Failed to initialize Vulkan Instance.");
                }
            } else {
                warn!("⚠️ [Hardware] Vulkan Loader NOT FOUND on Host.");
            }
        }

        HardwareTelemetry {
            total_ram_gb,
            used_ram_gb,
            total_vram_gb,
            used_vram_gb,
            gpu_name
        }
    }).clone()
}
