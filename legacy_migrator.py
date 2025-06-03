import os
import json
import subprocess

LEGACY_DIR = "legacy"
ENV_DIR = "environments/legacy_env"
os.makedirs(ENV_DIR, exist_ok=True)

config_path = os.path.join(LEGACY_DIR, "config.cfg")
with open(config_path, encoding="utf-16") as f:
    lines = f.readlines()

port = None
for line in lines:
    if line.startswith("PORT="):
        port = line.strip().split("=")[1]
        break

if port is None:
    raise ValueError("No se encontró la variable PORT")

run_script_path = os.path.join(LEGACY_DIR, "run.ps1")
with open(run_script_path) as f:
    run_script_content = f.read()


network_json = {
    "variable": {
        "port": {
            "type": "string",
            "default": port,
            "description": "Puerto del servidor local"
        }
    }
}

with open(os.path.join(ENV_DIR, "network.tf.json"), "w") as f:
    json.dump(network_json, f, indent=4)


main_json = {
    "resource": {
        "null_resource": {
            "legacy_server": {
                "triggers": {
                    "port": "${var.port}"
                },
                "provisioner": {
                    "local-exec": {
                        "command": f"echo 'Arrancando ${{var.port}}'"
                    }
                }
            }
        }
    }
}

with open(os.path.join(ENV_DIR, "main.tf.json"), "w") as f:
    json.dump(main_json, f, indent=4)


