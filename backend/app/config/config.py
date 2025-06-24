import os
from pathlib import Path


#===========================[GLOBAL CONFIG]

TELEGRAM_WEBHOOK = os.environ.get("TELEGRAM_WEBHOOK")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# ROOT_DATA_DIR = "~/projectrecon_data/"
# ROOT_DATA_DIR = os.path.expanduser(ROOT_DATA_DIR).rstrip('/')
# LOGS_DIR = f"{ROOT_DATA_DIR}/logs"
# PROGRAMS_DATA_FILE = f"{ROOT_DATA_DIR}/data_file.json"
CENTRAL_LOG_FILE = "logs.txt"

AVAILABLE_TESTS = ["subdomains_both", "urls_both", "js", "nuclei", "nmap"]


MONITOR_SCANS_PERIOD = 7200  # 2 hours interval

LOG_LEVEL_DEBUG = True

# DEV_MODE = os.getenv("DEV_MODE") == "1"
DEV_MODE = 1

if DEV_MODE:
    ROOT_DATA_DIR = "~/projectRecon-Data-Test"
    ROOT_DATA_DIR = os.path.expanduser(ROOT_DATA_DIR).rstrip('/')
    LOGS_DIR = f"{ROOT_DATA_DIR}/logs"
    PROGRAMS_DATA_FILE = f"{ROOT_DATA_DIR}/data_file.json"
    TOOLS_DIR = Path.home() / "tools"
    FRAMEWORK_DIR = Path.home() / "vsCode"
    BACKEND_DIR = f"{FRAMEWORK_DIR}/projectrecon"
    FRONTEND_DIR = f"{FRAMEWORK_DIR}/pentest-dashboard"
    PYTHON_ENV = ".dev_projectrecon_env"
    FRAMEWORK_SETUP_CONFIG = Path.home().joinpath(
        "vsCode", "projectrecon", "backend", "app", "config", "verify_setup.yaml"
    )
else:
    ROOT_DATA_DIR = "~/projectrecon/results"
    ROOT_DATA_DIR = os.path.expanduser(ROOT_DATA_DIR).rstrip('/')
    LOGS_DIR = f"{ROOT_DATA_DIR}/logs"
    PROGRAMS_DATA_FILE = f"{ROOT_DATA_DIR}/data_file.json"
    TOOLS_DIR = Path.home() / "tools"
    FRAMEWORK_DIR = Path.home() / "projectrecon"
    BACKEND_DIR = f"{FRAMEWORK_DIR}/projectrecon"
    FRONTEND_DIR = f"{FRAMEWORK_DIR}/pentest-dashboard"
    PYTHON_ENV = ".projectrecon_env"
    FRAMEWORK_SETUP_CONFIG = Path.home().joinpath(
        "projectrecon", "projectrecon", "backend", "app", "config", "verify_setup.yaml"
    )

#===========================[Files For Subdomain Enumeration]

#--- Passive tools
amass = "amass.txt"
subfinder = "subfinder.txt"
subdominator = "subdominator.txt"
cero = "cero.txt"
sublist3r = "sublist3r.txt"
yass = "yass.txt"
githubsubdomains = "githubsubdomains.txt"
gitlabsubdomains = "gitlabsubdomains.txt"
bbot = "bbot.txt"

#--- Active tools
alterx = "alterx.txt" # Filename to save results of active enumeration
dnsgen_Active_SubdomainResults = "dnsgen.txt" # Filename to save results of active enumeration
altdns_Active_SubdomainResults = "altdns.txt" # Filename to save results of active enumeration

#--- Resolvers File
puredns_ResolversFile = "~/.config/puredns/resolvers.txt" # Contains list of DNS resolvers
puredns_ResolversFile = os.path.expanduser(puredns_ResolversFile) # Getting Absolute path

#--- Organise
passive_subdomains = "passive_subdomains.txt" # Combined results of all passive tools
active_subdomains = "active_subdomains.txt" # Combined results of all active tools (These are resolved and valid subdomains)
subdomains_file = "subdomains.txt"
live_subdomains = "live_subdomains.txt" # This file contains only 200 OK subdomains
httpx_subdomains = "httpx_subdomains.json"


#===========================[Files For URL Enumeration]

#--- Passive enumeration
waybackurls='waybackurls.txt'
gau='gau.txt'
waymore='waymore.txt'
    
#--- Active enumeration
katana='katana.txt'
hakrawler='hakrawler.txt'
    
#--- Organise
urlsArranged200='urlsArranged200.txt'
extensions='extensions.txt'
live_extensions='live_extensions.txt'
urls_file='urls.txt'


#===========================[Files For JS Processing]

#--- JS Urls
js_urls='js_urls.txt'
getJS_urls='getJS_urls.txt'
extracted_urls='extracted_urls.txt'
extracted_paths='extracted_paths.txt'
sensitive_data='sensitive_data.txt'
sensitive_keywords='sensitive_keywords.txt'


#===========================[Files For Miscellaneous Processes]

nuclei_file='nuclei.txt'
xssResults='xss.txt'
openredirectResults='openRedirects.txt' 
ssrfResults='ssrfUrls.txt'