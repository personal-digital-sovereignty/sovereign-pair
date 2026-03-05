import os
import sys
import time

# Force Polling
os.environ["SENSUS_FORCE_POLLING"] = "true"

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.core.the_mom import should_use_polling, get_ignores, VaultWatcher

print("OS Sniffing Polling Result:", should_use_polling())

# Test ignores parser
os.makedirs("test_vault", exist_ok=True)
with open("test_vault/.sovereignignore", "w") as f:
    f.write("custom_ignore_dir\n")
    f.write("# comment\n")
    
ignores = get_ignores("test_vault")
assert "custom_ignore_dir" in ignores
assert "node_modules" in ignores
print("Ignores tested successfully:", ignores)

watcher = VaultWatcher("test_tenant", ["test_vault"])
print("Watcher instantiated. Using Polling:", watcher.use_polling)
watcher.start()

# Simulate a file creation to trigger Polling reset
print("Simulating file creation...")
with open("test_vault/dummy.md", "w") as f:
    f.write("test")

# Allow the poller to sweep a few times to show backoff
time.sleep(10)
watcher.stop()
print("Tests pass.")
