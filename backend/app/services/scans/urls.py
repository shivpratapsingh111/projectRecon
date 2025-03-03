from app.config.config  import *
import os
import subprocess
from app.interface.process_manager import run_commands
from app.logger.logger import setup_logger
from app.db.db_manager import DatabaseManager
from app.db.db_operations import DatabaseOperations
from app.config.db_config  import db_config
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)


logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)


def func_urls_ps(group_name, domain_list, execution_style, include_api, tool_selection, selected_tools, program_id, domain_id_list):
    logger.debug("Starting url enumeration")

    group_results = {}
    
    for domain, domain_id in zip(domain_list, domain_id_list):
        result_dir = f"{ROOT_DATA_DIR}/{group_name}/{domain}/urls"
        domain_dir = f"{ROOT_DATA_DIR}/{group_name}/{domain}"
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(f"{result_dir}/.logs", exist_ok=True)
        os.makedirs(f"{result_dir}/.tmp", exist_ok=True)


        cmd = {
            "waybackurls_cmd": f"cat {domain_dir}/subdomains/{subdomains_file} | waybackurls",

            "gau_cmd": f"cat {domain_dir}/subdomains/{subdomains_file} | gau",

            "waymore_cmd": f"waymore -n -xwm -urlr 0 -r 2 -i {domain} -mode U -oU {result_dir}/{waymore}",
            
            "katana_cmd":  f"katana --no-sandbox -u {domain_dir}/subdomains/{subdomains_file} -headless -no-color -depth 5 -aff -retry 2 -iqp -concurrency 5 -parallelism 5 -rate-limit 25 -xhr-extraction -js-crawl -known-files -extension-filter css,jpg,jpeg,png,svg,img,gif,mp4,flv,ogv,webm,webp,mov,mp3,m4a,m4p,scss,tif,tiff,ttf,otf,woff,woff2,bmp,ico,eot,htc,rtf,swf,image -o {result_dir}/{katana}",
            
            "hakrawler_cmd":  f"cat {domain_dir}/subdomains/{subdomains_file} | sed 's/^/https:\\/\\//' | hakrawler -d 5 -insecure -subs -t 5",            
        }



        all_commands = [
            (
                "waybackurls",
                f"{cmd.get('waybackurls_cmd')}",
                f"{result_dir}/{waybackurls}",
                f"{result_dir}/.logs/{waybackurls.removesuffix('.txt')}_stderr"
            ),
            (
                "gau",
                f"{cmd.get('gau_cmd')}",
                f"{result_dir}/{gau}",
                f"{result_dir}/.logs/{gau.removesuffix('.txt')}_stderr"
            ),
            (
                "waymore",
                f"{cmd.get('waymore_cmd')}",
                f"{result_dir}/.logs/{waymore}_stdout",
                f"{result_dir}/.logs/{waymore}_stderr"
            ),
            (
                "katana",
                f"{cmd.get('katana_cmd')}",
                f"{result_dir}/.logs/{katana.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{katana.removesuffix('.txt')}_stderr"
            ),
            (
                "hakrawler",
                f"{cmd.get('hakrawler_cmd')}",
                f"{result_dir}/{hakrawler}",
                f"{result_dir}/.logs/{hakrawler.removesuffix('.txt')}_stderr"
            )
        ]

        # Filter commands based on selected tools
        if tool_selection:
            commands = [cmd for cmd in all_commands if cmd[0] in selected_tools]
        else:
            commands = all_commands

        # Execute commands and store the result
        group_results[domain] = run_commands(group_name, domain, commands, program_id, domain_id, scan_dir="urls", execution_style=execution_style)

        # organise files
        command = f"cd {result_dir} ; cat {waybackurls} {gau} {waymore} {katana} {hakrawler} | sort -u >> {urls_file} ; mv {waybackurls} {gau} {waymore} {katana} {hakrawler} .tmp/"
        with open(f"{ROOT_DATA_DIR}/{group_name}/{central_log_file}" , "a") as writeLog:
            process = subprocess.Popen(
                command,
                # stdout=writeLog,
                stderr=writeLog,
                shell=True,
            )
            process.wait()

        logger.debug(f"URL Enum completed")

def organise_urls(group_name, domain_list, program_id, domain_id_list):
    group_results = {}
    
    for domain, domain_id in zip(domain_list, domain_id_list):
        logger.debug(f"Organising URL Enum for {domain}")
        result_dir = f"{ROOT_DATA_DIR}/{group_name}/{domain}/urls"
        
        commands = [
            (
                "Extracting JS Urls",
                f"""cd {result_dir} ; cat {urls_file} | grep -F .js | cut -d'?' -f1 | cut -d'#' -f1 | sort -u >> {js_urls}""",
                f"{ROOT_DATA_DIR}/{group_name}/{central_log_file}",
                f"{ROOT_DATA_DIR}/{group_name}/{central_log_file}"
            ),
            (
                f"Extensions",
                f"""
                    categories=("ext" "text" "juicy" "docs" "code" "cert" "binaries" "archives")
                    for category in "${{categories[@]}}"; do
                        success_file="{result_dir}/{live_extensions}"
                        failure_file="{result_dir}/{extensions}"

                        # Get the URLs for the current category
                        category_urls=$(cat {result_dir}/{urls_file} | gf "$category" | cut -d'?' -f1 | cut -d'#' -f1 | sort -u | httpx -status-code -no-color -silent)

                        # If there are URLs for the category, add the category label at the top
                        if [ -n "$category_urls" ]; then
                            count=$(echo "$category_urls" | wc -l)
                            echo "[${{category}}] [${{count}}]" >> "$success_file"
                            echo "[${{category}}] [${{count}}]" >> "$failure_file"

                            # Process each URL for the category
                            echo "$category_urls" | while read -r url_status; do
                                # Extract URL and status code from the output (status is in square brackets)
                                url=$(echo "$url_status" | awk '{{print $1}}')
                                status=$(echo "$url_status" | awk -F'[][]' '{{print $2}}')
                                if [ "$status" -eq 200 ]; then
                                    echo "$url [$status]" >> "$success_file"
                                else
                                    echo "$url [$status]" >> "$failure_file"
                                fi
                            done
                        fi
                    done
                """,
                f"{result_dir}/.logs/extensions_stdout",
                f"{result_dir}/.logs/extensions_stderr"
            )
        ]
        # Execute commands and store the result
        group_results[domain] = run_commands(group_name, domain, commands, program_id, domain_id, scan_dir="urls", execution_style="sequential")

        logger.debug(f"Urls arranged for {domain}")


def start_urls_scan(group_name, domain_list, execution_style, config, program_id, domain_id_list):

    url_enum = config
    
    if not url_enum.get("run", False):
        print("Subdomain enumeration is disabled.")
        return
    include_api = url_enum.get("includeApi", False)
    tool_selection = url_enum.get("toolSelection", False)
    selected_tools = url_enum.get("selectedTools", [])

    func_urls_ps(group_name, domain_list, execution_style, include_api, tool_selection, selected_tools, program_id, domain_id_list)
    organise_urls(group_name,domain_list, program_id, domain_id_list)
    logger.info("URL enumration completed.")