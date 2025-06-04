import os
import json
import zlib
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REGENERATE_SCRIPT = os.path.join(SCRIPT_DIR, "..", "generate_envs.py")
SNAPSHOT_FILE = os.path.join(SCRIPT_DIR, "snapshot.bin")
WATCHED_DIR = os.path.join(SCRIPT_DIR, "modules", "simulated_apps")

def take_snapshot(directory):
    snapshot = {}
    for root, _, files in os.walk(directory):
        for f in files:
            path = os.path.join(root, f)
            try:
                stat = os.stat(path)
                snapshot[path] = stat.st_mtime
            except Exception:
                pass
    return snapshot

def compress_snapshot(snapshot):
    json_data = json.dumps(snapshot)
    return zlib.compress(json_data.encode("utf-8"))

def decompress_snapshot(data):
    json_data = zlib.decompress(data).decode("utf-8")
    return json.loads(json_data)

def load_previous_snapshot():
    if not os.path.exists(SNAPSHOT_FILE):
        return None
    with open(SNAPSHOT_FILE, "rb") as f:
        data = f.read()
        return decompress_snapshot(data)

def save_snapshot(snapshot):
    data = compress_snapshot(snapshot)
    with open(SNAPSHOT_FILE, "wb") as f:
        f.write(data)

def regenerate():
    print("¡Cambios detectados! Regenerando...")
    subprocess.run(["python", REGENERATE_SCRIPT])
    print("Regeneración completada")

def main():
    current_snapshot = take_snapshot(WATCHED_DIR)
    previous_snapshot = load_previous_snapshot()

    if previous_snapshot != current_snapshot:
        regenerate()
        save_snapshot(current_snapshot)
    else:
        print("No se detectaron cambios. No se regenera nada.")

if __name__ == "__main__":
    main()
