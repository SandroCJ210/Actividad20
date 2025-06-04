import os, json
from shutil import copyfile
from jsonschema import validate, ValidationError
api_key = os.environ.get("API_KEY")
#if api_key is None:
#    raise Exception("No se obtuvo la variable de entorno API_KEY")

# Parámetros de ejemplo para N entornos
ENVS = []
for i in range(1, 11):
    if i == 3:
        env = {"name": f"app{i}", "network": "net2-peered"}
    else:
        env = {"name": f"app{i}", "network": f"net{i}"}
    ENVS.append(env)

MODULE_DIR = "modules/simulated_app"
OUT_DIR    = "environments"

with open("modules/simulated_app/network_schema.json") as f:
    network_schema = json.load(f)

with open("modules/simulated_app/main_schema.json") as f:
    main_schema = json.load(f)

def render_and_write(env):
    env_dir = os.path.join(OUT_DIR, env["name"])
    os.makedirs(env_dir, exist_ok=True)

    for f in ["network.tf.json", "main.tf.json"]:
        fpath = os.path.join(env_dir, f)
        if os.path.exists(fpath):
            os.remove(fpath)
            
    # 1) Copia la definición de variables (network.tf.json)
    network_dst = os.path.join(env_dir, "network.tf.json")
    copyfile(
        os.path.join(MODULE_DIR, "network.tf.json"),
        os.path.join(env_dir, "network.tf.json")
    )

    with open(network_dst) as f:
        network_data = json.load(f)
    try:
        validate(instance=network_data, schema=network_schema)
        print(f"network.tf.json válido para {env['name']}")
    except ValidationError as e:
        print(f"Error en network.tf.json para {env['name']}: {e.message}")
        exit(1)

    # 2) Genera main.tf.json SÓLO con recursos
    config = {
        "resource": [
            {
                "null_resource": [
                    {
                        "local_server": [
                            {
                                "triggers": {
                                    "name":    env["name"],
                                    "network": env["network"],
                                    "port": "${var.port}"
                                },
                                "provisioner": [
                                    {
                                        "local-exec": {
                                            "command": (
                                                f"echo 'Arrancando servidor "
                                                f"{env['name']} en red {env['network']}'"
                                                "en el puerto ${var.port}"
                                            )
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    try:
        validate(instance=config, schema=main_schema)
        print(f"main.tf.json válido para {env['name']}")
    except ValidationError as e:
        print(f"Error en main.tf.json para {env['name']}: {e.message}")
        exit(1)

    with open(os.path.join(env_dir, "main.tf.json"), "w") as fp:
        json.dump(config, fp, sort_keys=True, indent=4)

if __name__ == "__main__":
    # Limpia entornos viejos (si quieres)

    for env in ENVS:
        render_and_write(env)
    print(f"Generados {len(ENVS)} entornos en '{OUT_DIR}/'")
