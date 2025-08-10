# External imports
from psycopg2.extras import execute_values
import subprocess, psycopg2, json, os

# External imports
from app.interface.process_manager import run_commands
from app.interface.logger_manager import setup_logger
from app.interface.database_manager import db_ops
from app.config.db_config  import DB_CONFIG
from app.config.config import (
    ROOT_DATA_DIR,
	LOG_LEVEL_DEBUG,
    CENTRAL_LOG_FILE,
    passive_subdomains,
    active_subdomains,
    subdomains_file,
    live_subdomains,
    subdominator,
    subfinder,
    cero,
    sublist3r,
    yass,
    githubsubdomains,
    gitlabsubdomains,
    bbot,
    alterx,
    httpx_subdomains,
    puredns_ResolversFile,
)

# Initialization
logger = setup_logger(__name__, log_file_path='service', enable_debug = LOG_LEVEL_DEBUG)
program_results = {}


# Logic
def organise_subdomains(program_name, domain_list, program_uuid, target_uuid_list, httpx, screenshot):

    for domain, target_uuid in zip(domain_list, target_uuid_list):
        result_dir = f"{ROOT_DATA_DIR}/{program_name}/{domain}/subdomains"
        logger.debug(f"Starting to organise Subdomain Enum for {domain}")

        commands = [
            (
                "Organising_Subdomains", 
                f"""cd {result_dir} ; cat {passive_subdomains} {active_subdomains} | awk '{{print $1}}' | awk '{{print tolower($0)}}' | grep -iE "^(.*\\.)?{domain}$" | sed 's/^[^a-zA-Z0-9]*//' | sed -E 's#^https?://##; s#^www*\\.##' | sort -u >> {subdomains_file} ; mv {passive_subdomains} {active_subdomains} bbot/ .tmp/ ; sort -u {subdomains_file} -o {subdomains_file}""",
                f"{ROOT_DATA_DIR}/{program_name}/{CENTRAL_LOG_FILE}", 
                f"{ROOT_DATA_DIR}/{program_name}/{CENTRAL_LOG_FILE}"
            )
        ]
        # Add Httpx Subdomains only if `httpx` is True
        if httpx:
            commands.append(
                (
                    "Httpx_Subdomains", 
                    f"""cd {result_dir} ; cat {subdomains_file} | /usr/bin/httpx -server -td -sc -title -json -o httpx_subdomains.json 2> /dev/null ; cat httpx_subdomains.json | jq -r 'select(.status_code == 200) | .url' > {live_subdomains}""", 
                    f"{ROOT_DATA_DIR}/{program_name}/{CENTRAL_LOG_FILE}", 
                    f"{ROOT_DATA_DIR}/{program_name}/{CENTRAL_LOG_FILE}"
                )
            )

        # Add Screenshot Subdomains only if `screenshot` is True
        if screenshot:
            commands.append(
                (
                    "Screenshot Subdomains",
                    f"cd {result_dir} ; nuclei -l {subdomains_file} -rate-limit 25 -bulk-size 5 -concurrency 5 -headless-bulk-size 3 -headless-concurrency 3 -js-concurrency 3 -probe-concurrency 10 -headless -t ~/nuclei-templates/headless/screenshot.yaml",
                    f"{ROOT_DATA_DIR}/{program_name}/{CENTRAL_LOG_FILE}", 
                    f"{ROOT_DATA_DIR}/{program_name}/{CENTRAL_LOG_FILE}"
                )
            )

        program_results[domain] = run_commands(program_name, domain, commands, program_uuid, target_uuid, scan_dir="subdomains", execution_style="sequential")
        logger.debug(f"Organising Subdomains [Completed] [{domain}]")
        if httpx:
            logger.debug(f"Httpx Subdomains [Completed] [{domain}]")
        if screenshot:
            logger.debug(f"Screenshot [Completed] [{domain}]")

# ---

def func_subdomains_ps(program_name, domain_list, execution_style, include_api, tool_selection, selected_tools, program_uuid, target_uuid_list):
    program_results = {}
    
    for domain, target_uuid in zip(domain_list, target_uuid_list):
        result_dir = f"{ROOT_DATA_DIR}/{program_name}/{domain}/subdomains"
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(f"{result_dir}/.logs", exist_ok=True)
        os.makedirs(f"{result_dir}/.tmp", exist_ok=True)

        cmd = {
            "bbot_cmd": f"bbot -t {domain} -f subdomain-enum -n bbot -o {result_dir} -y --modules asn azure_realm azure_tenant baddns_direct baddns_zone dnsbimi dnscaa dnscommonsrv github_codesearch github_org httpx hunterio crt_db ipneighbor oauth otx postman postman_download securitytxt shodan_dns sslcert subdomainradar --exclude-modules dnsbrute dnsbrute_mutations wayback",

            "subdominator_cmd": f"subdominator -d {domain} --no-color --disable-update-check -o {result_dir}/{subdominator}" + (" --config-path ~/.config/projectRecon/api-subdominator.txt" if include_api else ""),

            # "subfinder_cmd": f"subfinder -d {domain} -sources chinaz,columbus,github,hunter,robtex,threatbook,whoisxmlapi,zoomeyeapi,virustotal,shodan,securitytrails,fofa,chaos,certspotter,censys,binaryedge,bevigil -no-color -disable-update-check -o {result_dir}/{subfinder}" + (" -provider-config ~/.config/projectRecon/api-subfinder.txt" if include_api else ""),

            "subfinder_cmd": f"subfinder -d {domain} -no-color -disable-update-check -o {result_dir}/{subfinder}" + (" -provider-config ~/.config/projectRecon/api-subfinder.txt" if include_api else ""),
            
            "cero_cmd": f"cero {domain} | tee -a {result_dir}/{cero}",
            
            "sublist3r_cmd": f"cd ~/tools/Sublist3r ; python3 sublist3r.py -d {domain} -o {result_dir}/{sublist3r}",
            
            "yass_cmd": f"yass {domain} -nc | tee -a {result_dir}/{yass}",
            
            "githubsubdomains_cmd": f"github-subdomains -d {domain} -raw -o {result_dir}/{githubsubdomains}",
            
            "gitlabsubdomains_cmd": f"github-subdomains -d {domain} | tee -a {result_dir}/{gitlabsubdomains}",
        }
    
        all_commands = [
            (
                "bbot",
                f"{cmd.get('bbot_cmd')}",
                f"{result_dir}/.logs/{bbot.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{bbot.removesuffix('.txt')}_stderr"
            ),
            (
                "subdominator",
                f"{cmd.get('subdominator_cmd')}",
                f"{result_dir}/.logs/{subdominator.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{subdominator.removesuffix('.txt')}_stderr"
            ),
            (
                "subfinder",
                f"{cmd.get('subfinder_cmd')}",
                f"{result_dir}/.logs/{subfinder.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{subfinder.removesuffix('.txt')}_stderr"
            ),
            (
                "cero",
                f"{cmd.get('cero_cmd')}",
                f"{result_dir}/.logs/{cero.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{cero.removesuffix('.txt')}_stderr"
            ),
            (
                "sublist3r",
                f"{cmd.get('sublist3r_cmd')}",
                f"{result_dir}/.logs/{sublist3r.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{sublist3r.removesuffix('.txt')}_stderr"
            ),
            (
                "yass",
                f"{cmd.get('yass_cmd')}",
                f"{result_dir}/.logs/{yass.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{yass.removesuffix('.txt')}_stderr"
            ),
            (
                "githubsubdomains",
                f"{cmd.get('githubsubdomains_cmd')}",
                f"{result_dir}/.logs/{githubsubdomains.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{githubsubdomains.removesuffix('.txt')}_stderr"
            ),
            (
                "gitlabsubdomains",
                f"{cmd.get('gitlabsubdomains_cmd')}",
                f"{result_dir}/.logs/{gitlabsubdomains.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{gitlabsubdomains.removesuffix('.txt')}_stderr"
            )
        ]

        
        if tool_selection:
            commands = [cmd for cmd in all_commands if cmd[0] in selected_tools]
        else:
            commands = all_commands
            
        program_results[domain] = run_commands(program_name, domain, commands, program_uuid, target_uuid, scan_dir="subdomains", execution_style=execution_style)
 
    
        command = f"cd {result_dir} ; cp bbot/subdomains.txt {bbot} ; cat {bbot} {subdominator} {subfinder} {cero} {sublist3r} {yass} {githubsubdomains} {gitlabsubdomains} > {passive_subdomains} ; sort -u {passive_subdomains} -o {passive_subdomains} ; mv {bbot} {subdominator} {subfinder} {cero} {sublist3r} {yass} {githubsubdomains} {gitlabsubdomains} .tmp/" 
        
        with open(f"{ROOT_DATA_DIR}/{program_name}/{CENTRAL_LOG_FILE}" , "a") as writeLog:
            process = subprocess.Popen(
                command,
                # stdout=writeLog,
                stderr=writeLog,
                shell=True,
            )
            process.wait()
        logger.info(f"Passive Subdomains completed for {domain}")

# ---

def func_subdomains_ac(program_name, domain_list, execution_style, program_uuid, target_uuid_list):
    program_results = {}
    
    for domain, target_uuid in zip(domain_list, target_uuid_list):
        result_dir = f"{ROOT_DATA_DIR}/{program_name}/{domain}/subdomains"
        os.makedirs(result_dir, exist_ok=True)
        
        # First command: alterx processing
        commands = [
            (
                "alterx",
                f"cat {result_dir}/{passive_subdomains} | alterx | tee -a {result_dir}/{alterx}", 
                f"{result_dir}/.logs/{alterx.removesuffix('.txt')}_stdout", 
                f"{result_dir}/.logs/{alterx.removesuffix('.txt')}_stderr"
            )
        ]
        program_results[domain] = run_commands(program_name, domain, commands, program_uuid, target_uuid, scan_dir="subdomains", execution_style=execution_style)
        
        # Second command: DNS resolver (DO NOT MERGE THIS IN ABOVE ONE: this command will resolve permuted subdomains, so it has to run only after permutations has done)
        commands = [
            (
                "dnsresolver",
                f"cd {result_dir} ; cat {alterx} | dnsresolver --resolvers {puredns_ResolversFile} -t 3 -c 100 -r 100 | tee -a {active_subdomains} ; mv {alterx} .tmp/",
                f"{result_dir}/.logs/{active_subdomains}_stdout",
                f"{result_dir}/.logs/{active_subdomains}_stderr"
            )
        ]
        program_results[f"{domain}_dnsresolver"] = run_commands(program_name, domain, commands, program_uuid, target_uuid, scan_dir="subdomains", execution_style="sequential")
        
        logger.info(f"Active Subdomains completed for {domain}")

# ---

def read_subdomains_from_file(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip()]

# ---

def update_subdomains_to_db(program_name, domain_list):
    batch_size=10000
    insert_query = """
        INSERT INTO web_targets (program_uuid, target_domain) 
        VALUES %s 
        ON CONFLICT (target_domain) DO NOTHING
    """
    for domain in domain_list:
        
        file_path = f"{ROOT_DATA_DIR}/{program_name}/{domain}/subdomains/{subdomains_file}"

        if os.path.exists(file_path):
            subdomains = read_subdomains_from_file(file_path)
            program_uuid = str(db_ops.query_operations().get_program_uuid(program_name))

            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cursor:
                   
                    for i in range(0, len(subdomains), batch_size):
                        chunk = subdomains[i:i + batch_size]
                        values = [(str(program_uuid), sub) for sub in chunk]
                        
                        execute_values(cursor, insert_query, values)
                        logger.debug(f"Inserted {len(values)} records...")
                    
                    conn.commit()
                    logger.debug(f"All subdomains inserted in DB. [Count: {len(subdomains)}]")

# ---

def read_jsonl_file(file_path):
    with open(file_path, "r") as file:
        return [json.loads(line) for line in file]

# ---

def update_httpx_subdomains_to_db(program_name, domain_list):
    for domain in domain_list:
        file_path = f"{ROOT_DATA_DIR}/{program_name}/{domain}/subdomains/{httpx_subdomains}"
        
        try:
            if os.path.exists(file_path):
                subdomains_data = read_jsonl_file(file_path)
                for entry in subdomains_data:
                    values = (
                        entry.get("tech", []),
                        entry.get("status_code"),
                        entry.get("port"),
                        entry.get("host"),
                        entry.get("a", []),
                        entry.get("aaaa", []),
                        entry.get("time"),
                        entry.get("webserver"),
                        entry.get("input")
                    )
                    db_ops.update_operations().update_web_targets_data(values)
        except Exception as e:
            logger.exception(f"Error occured while updating HTTPX subdomains data. {e}")        
            logger.debug(f"All subdomains data updated to DB. [Count: {len(subdomains_data)}]")

 # ---
            
def start_subdomains_scan(program_name, domain_list, execution_style, config, program_uuid, target_uuid_list):
    subdomain_enum = config
    
    if not subdomain_enum.get("run", False):
        logger.warning("Subdomain enumeration is disabled.")
        return
    include_api = subdomain_enum.get("includeApi", False)
    tool_selection = subdomain_enum.get("toolSelection", False)
    httpx = subdomain_enum.get("httpx", False)
    screenshot = subdomain_enum.get("screenshot", False)
    selected_tools = subdomain_enum.get("selectedTools", [])

    logger.debug("Checking program details in DB")
    
    logger.debug("Executing: start_subdomains_scan")
    func_subdomains_ps(program_name, domain_list, execution_style, include_api, tool_selection, selected_tools, program_uuid, target_uuid_list)
    
    if subdomain_enum.get("dnsBruteforce", False):
        func_subdomains_ac(program_name, domain_list, execution_style, program_uuid, target_uuid_list)
    
    organise_subdomains(program_name, domain_list, program_uuid, target_uuid_list, httpx, screenshot)
    update_subdomains_to_db(program_name, domain_list)
    if httpx:
        update_httpx_subdomains_to_db(program_name, domain_list)