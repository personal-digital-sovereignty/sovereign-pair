use ash::{vk, Entry};
use std::ffi::CStr;

fn main() {
    unsafe {
        if let Ok(entry) = Entry::load() {
            let app_info = vk::ApplicationInfo::default().api_version(vk::make_api_version(0, 1, 0, 0));
            let create_info = vk::InstanceCreateInfo::default().application_info(&app_info);
            
            if let Ok(instance) = entry.create_instance(&create_info, None) {
                if let Ok(pdevices) = instance.enumerate_physical_devices() {
                    for (i, &pdevice) in pdevices.iter().enumerate() {
                        let props = instance.get_physical_device_properties(pdevice);
                        let name_cstr = CStr::from_ptr(props.device_name.as_ptr());
                        let name = name_cstr.to_string_lossy();
                        
                        let mem_props = instance.get_physical_device_memory_properties(pdevice);
                        let mut total_vram = 0;
                        for i in 0..mem_props.memory_heap_count {
                            let heap = mem_props.memory_heaps[i as usize];
                            if heap.flags.contains(vk::MemoryHeapFlags::DEVICE_LOCAL) {
                                total_vram += heap.size;
                            }
                        }
                        println!("GPU {}: {} -> VRAM: {} GB", i, name, total_vram / 1024 / 1024 / 1024);
                    }
                }
                instance.destroy_instance(None);
            }
        }
    }
}
