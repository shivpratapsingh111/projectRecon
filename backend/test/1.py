import json
from app.services.scans.urls import start_urls_scan
from app.services.scans.subdomains import start_subdomains_scan
from app.services.scans.subdomains import func_subdomains_ps_only

config_string = """
{
    "subdomainEnum":
    {
        "run": true,
        "includeApi": false,
        "toolSelection": true,
        "selectedTools":
        [
            "bbot",
            "subdominator",
            "subfinder",
            "githubsubdomains",
            "gitlabsubdomains"
        ],
        "isPassive": true,
        "dnsBruteforce": false
    },
    "urlEnum":
    {
        "run": true,
        "includeApi": true,
        "toolSelection": true,
        "selectedTools":
        [
            "waybackurls"
        ],
        "isPassive": true,
        "isActivePassive": false
    },
    "nuclei":
    {
        "run": false,
        "allTemplates": false,
        "specificTemplates": false,
        "templateInput": "",
        "customTemplates": false,
        "specificCommand": false,
        "commandInput": ""
    },
    "nmap":
    {
        "run": false,
        "allPorts": false,
        "topPorts": false,
        "webPorts": false,
        "specificPorts": false,
        "portInput": "",
        "specificCommand": false,
        "commandInput": ""
    },
    "js":
    {
        "run": true,
        "doEverything": true,
        "specificRegex": false,
        "regexInput": "",
        "regexOnly": false
    }
}
"""
def subdomains():
    print("Running subdomains...")

def urls():
    print("Running urls...")

def nmap():
    print("Running nmap...")

def js():
    print("Running js...")

def nuclei():
    print("Running nuclei...")

def run_scans(group_name, domain_list, execution_style, scan_config):
    
    subdomain_enum = scan_config.get("subdomainEnum", {})
    url_enum = scan_config.get("urlEnum", {})
    nuclei_enum = scan_config.get("nuclei", {})
    nmap_enum = scan_config.get("nmap", {})
    js_enum = scan_config.get("js", {})
    
    if not subdomain_enum.get("run", False):
        print("Subdomain enumeration is disabled.")
    else:
        subdomains()
        start_subdomains_scan(group_name, domain_list, execution_style, subdomain_enum)

    if not url_enum.get("run", False):
        print("url_enum is disabled.")
    else:
        urls()
        start_urls_scan(group_name, domain_list, execution_style, url_enum)

    if not nuclei_enum.get("run", False):
        print("nuclei is disabled.")
    else:
        nuclei()

    if not nmap_enum.get("run", False):
        print("nmap is disabled.")
    else:
        nmap()

    if not js_enum.get("run", False):
        print("js is disabled.")
    else:
        js()


config = json.loads(config_string)
run_scans(group_name="group-1", domain_list=['thecyberboy.com'], execution_style="parallel", scan_config=config)