# External imports
import os, subprocess, yaml, requests
from pathlib import Path

# Internal imports
from app.config.config import TOOLS_DIR, FRAMEWORK_DIR, PYTHON_ENV, FRAMEWORK_SETUP_CONFIG

# Initialization
ALLSET = True

# Logic
def load_config(path=FRAMEWORK_SETUP_CONFIG):
    with open(path) as f:
        return yaml.safe_load(f)

# ---

def detect_os():
    # returns tuple (family, distro, version)
    data = {}
    with open("/etc/os-release") as f:
        for line in f:
            if "=" in line:
                k, v = line.rstrip().split("=", 1)
                data[k] = v.strip('"')
    
    distro = data.get("ID", "").lower()
    version = data.get("VERSION_ID", "")
    family = data.get("ID_LIKE", "").split()[0].lower() if data.get("ID_LIKE") else distro
    return family, distro, version

# ---

def check_system_packages(cfg, family, distro):
    pkgs = []
    if distro in cfg["os"]:
        pkgs = cfg["os"][distro]["packages"]
    elif family in cfg["os"]:
        pkgs = cfg["os"][family]["packages"]
    missing = []
    for pkg in pkgs:
        cmd = {
          "debian": ["dpkg", "-s", pkg],
          "ubuntu": ["dpkg", "-s", pkg],
          "fedora": ["rpm", "-q", pkg],
          "arch": ["pacman", "-Qi", pkg]
        }[family]
        if subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
            missing.append(pkg)
    return missing

# ---

def check_tools(cfg):
    missing = []
    # custom_setup
    for tool in cfg["tools"]["custom_setup"]:
        if not (Path(TOOLS_DIR) / tool).exists():
            missing.append(tool)
    # others
    for pkg in cfg["tools"]["others"]:
        if subprocess.call(["which", pkg], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) != 0:
            missing.append(pkg)
    return missing

# ---

def check_env_vars(cfg):
    return [v for v in cfg["env_vars"] if v not in os.environ]

# ---

def check_python_venv():
    return Path.home().joinpath(f"{PYTHON_ENV}/bin/activate").exists()

# ---

def check_github_updates(cfg):
    updates = []
    for repo in cfg["github_repos"]:
        r = requests.get(repo["url"] + "/commits/main")
        r.raise_for_status()
        latest_sha = r.json()["sha"]
        # compare to local clone:
        local = subprocess.check_output(
            ["git", "-C", (Path(FRAMEWORK_DIR) / repo["name"]), "rev-parse", "HEAD"]
        ).decode().strip()
        if latest_sha != local:
            updates.append(repo["name"])
    return updates

# ---

def check_postgres(cfg, family):
    errs = []
    global is_postgres_functional
    try:
        subprocess.check_call(
            ["psql", "-U", cfg["postgres"]["user"], "-c", "\\q"],
            env={**os.environ, "PGPASSWORD": cfg["postgres"]["password"]}
        )
        is_postgres_functional = True
    except Exception as e:
        errs.append(f"cannot connect to postgres as user: {e}")
        is_postgres_functional = False
    return errs, is_postgres_functional

# ---

def verify_setup():
    cfg = load_config()
    family, distro, version = detect_os()

    missing_system_packages = check_system_packages(cfg, family, distro)
    env_vars = check_env_vars(cfg)
    missing_tools = check_tools(cfg)
    python_venv = check_python_venv()
    updates = check_github_updates(cfg)
    pg_errs, pg_ok = check_postgres(cfg, family)

    ALLSET = (
        not missing_system_packages and
        not env_vars and
        not missing_tools and
        python_venv and
        pg_ok
    )

    if not ALLSET:
        return {
            "status": True,
            "message": "Some required things to run scan are not found",
            "data": {
                "os": {"distro": distro, "family": family},
                "missing_system_packages": missing_system_packages or None,
                "unset_env_vars": env_vars or None,
                "python_environment": python_venv,
                "updates": updates or False,
                "missing_tools": missing_tools or None,
                "postgresql": pg_errs or True,
            },
        }
    else:
        return {
            "status": True,
            "message": "Everything is installed"
        }

# if __name__ == "__main__":
#     result = main()
#     print(json.dumps(result, indent=2))
