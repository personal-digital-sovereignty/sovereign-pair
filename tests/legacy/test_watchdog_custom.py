import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CustomWatcher(FileSystemEventHandler):
    def __init__(self, observer, ignores):
        self.observer = observer
        self.ignores = ignores

    def schedule_recursively(self, base_path):
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in self.ignores]
            print("Scheduling:", root)
            self.observer.schedule(self, root, recursive=False)

    def on_created(self, event):
        if event.is_directory:
            name = os.path.basename(event.src_path)
            if name not in self.ignores:
                print("New permitted dir discovered! Scheduling:", event.src_path)
                self.observer.schedule(self, event.src_path, recursive=False)
        else:
            print("File created:", event.src_path)

if __name__ == "__main__":
    os.makedirs("test_vault/node_modules", exist_ok=True)
    os.makedirs("test_vault/good_dir", exist_ok=True)
    
    obs = Observer()
    watcher = CustomWatcher(obs, ["node_modules", ".git", ".venv", ".obsidian"])
    watcher.schedule_recursively("test_vault")
    obs.start()
    
    # Simulate writing
    time.sleep(1)
    with open("test_vault/node_modules/ignore.md", "w") as f:
        f.write("ignore")
    with open("test_vault/good_dir/keep.md", "w") as f:
        f.write("keep")
        
    os.makedirs("test_vault/new_node_modules", exist_ok=True)
    time.sleep(1)
    obs.stop()
    obs.join()
