import datetime, time, subprocess
from app.config.config  import *
from app.interface.process_manager import run_commands
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)

group_results = {}

# DO NOT REMOVE PARAMETER: `execution_style`
def start_js_scan(group_name, domain_list, execution_style, nuclei_enum, program_id, domain_id_list):
    # Store results for each domain
    group_results = {}
    
    # Execute commands for a group of domains
    for domain, domain_id in zip(domain_list, domain_id_list):
        result_dir = f"{ROOT_DATA_DIR}/{group_name}/{domain}/js"
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(f"{result_dir}/.logs", exist_ok=True)
        os.makedirs(f"{result_dir}/jsfiles", exist_ok=True)
        commands = [
            # (
            #     "getJS",
            #     f"getJS -input {ROOT_DATA_DIR}/{group_name}/{domain}/subdomains/{subdomains_file} -output {result_dir}/{getJS_urls}",
            #     f"{result_dir}/.logs/{getJS_urls.removesuffix('.txt')}_stdout",
            #     f"{result_dir}/.logs/{getJS_urls.removesuffix('.txt')}_stderr"
            # ),
            # (
            #     "Downloading JS files",
            #     f"cp {ROOT_DATA_DIR}/{group_name}/{domain}/urls/{js_urls} {result_dir}/{js_urls} && cat {result_dir}/{js_urls} {result_dir}/{getJS_urls} | sort -u -o {result_dir}/{js_urls} && fetcher -f {result_dir}/{js_urls} -dir {result_dir}/jsfiles -t 10",
            #     f"{result_dir}/.logs/downloading_js_files_stdout",
            #     f"{result_dir}/.logs/downloading_js_files_stderr"
            # ),
            (
                "Extracting Urls",
                # f"cat {result_dir}/jsfiles/* | gf urls | tee -a {result_dir}/{extracted_urls}",
                f"cd {result_dir}/jsfiles/ && cat * | gf urls >> {result_dir}/{extracted_urls}",
                f"{result_dir}/.logs/{extracted_urls.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{extracted_urls.removesuffix('.txt')}_stderr"
            ),
            (
                "Extracting Paths",
                f"cd {result_dir}/jsfiles/ && cat * | gf path >> {result_dir}/{extracted_paths} ; cat * | gf paths >> {result_dir}/{extracted_paths} ; sort -u {result_dir}/{extracted_paths} -o {result_dir}/{extracted_paths}",
                f"{result_dir}/.logs/{extracted_paths.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{extracted_paths.removesuffix('.txt')}_stderr"
            ),
            (
                "Extracting Sensitive Data",
                f"cd {result_dir}/jsfiles/ && cat * | gf secrets >> {result_dir}/{sensitive_data}",
                f"{result_dir}/.logs/{sensitive_data.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{sensitive_data.removesuffix('.txt')}_stderr"
            ),
            # (
            #     "Extracting Sensitive Keywords",
            #     f"python3 ~/tools/Find-In-Js/findInJs.py -dir {result_dir}/jsfiles/ -r ~/tools/Find-In-Js/usethese/sensitive_keywords.txt -o {result_dir}/{sensitive_keywords}",
            #     f"{result_dir}/.logs/{sensitive_keywords.removesuffix('.txt')}_stdout",
            #     f"{result_dir}/.logs/{sensitive_keywords.removesuffix('.txt')}_stderr"
            # ),
            (
                "Nuclei",
                f"nuclei -l {ROOT_DATA_DIR}/{group_name}/{domain}/js/{js_urls} -t ~/nuclei-templates/exposures/ -o {result_dir}/{nuclei_file} ; cat {result_dir}/{nuclei_file} >> {ROOT_DATA_DIR}/{group_name}/{domain}/nuclei/{nuclei_file}",
                f"{result_dir}/.logs/{nuclei_file.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{nuclei_file.removesuffix('.txt')}_stderr"
            )
        ]
        
        # Execute commands and store the result
        group_results[domain] = run_commands(group_name, domain, commands, program_id, domain_id, scan_dir="nuclei", execution_style="sequential")
 
    logger.info(f"JS scan completed")
