import os
import time
import glob
from build import compile_presentation

base_dir = os.path.dirname(os.path.abspath(__file__))

def get_mtimes():
    mtimes = {}
    patterns = [
        os.path.join(base_dir, "styles", "*"),
        os.path.join(base_dir, "components", "*"),
        os.path.join(base_dir, "slides", "*"),
        os.path.join(base_dir, "scripts", "*"),
        os.path.join(base_dir, "assets", "*"),
        os.path.join(base_dir, "build.py"),
    ]
    for p in patterns:
        for f in glob.glob(p):
            if os.path.isfile(f):
                try:
                    mtimes[f] = os.path.getmtime(f)
                except Exception:
                    pass
    return mtimes

def main():
    print("[Watcher] Auto-recompile watcher started...", flush=True)
    last_mtimes = get_mtimes()
    while True:
        time.sleep(0.8)
        current_mtimes = get_mtimes()
        if current_mtimes != last_mtimes:
            print("[Watcher] Detected file change, recompiling presentation...", flush=True)
            try:
                compile_presentation()
            except Exception as e:
                print(f"[Watcher] Error during compilation: {e}", flush=True)
            last_mtimes = current_mtimes


if __name__ == "__main__":
    main()
