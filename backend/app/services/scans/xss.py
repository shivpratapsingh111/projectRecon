# External imports
import os

# Internal imports
from app.config.config import ROOT_DATA_DIR, LOG_LEVEL_DEBUG, urls_file, xssResults
from app.interface.process_manager import run_commands
from app.interface.logger import setup_logger

logger = setup_logger(__name__, log_file_path="service", enable_debug=LOG_LEVEL_DEBUG)

# Initialization
program_results = {}


# Logic
def func_xss_run(program_name, domain_list):

    # Store results for each domain
    program_results = {}

    # Execute commands for a program of domains
    for domain in domain_list:
        result_dir = f"{ROOT_DATA_DIR}/{program_name}/{domain}/xss"
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(f"{result_dir}/.logs", exist_ok=True)
        commands = [
            (
                "xss",
                f"""cat {ROOT_DATA_DIR}/{program_name}/{domain}/{urls_file} | grep = | kxss""",
                f"{result_dir}/{xssResults}",
                f"{result_dir}/.logs/{xssResults.removesuffix('.txt')}_stderr",
            )
        ]

        # Execute commands and store the result
        program_results[domain] = run_commands(
            program_name, domain, commands, scan_dir="xss", execution_style="sequential"
        )
        logger.info(f"[SCAN - XSS] COMPLETED [{program_name} - {domain}]")

    logger.info(f"[SCAN - XSS] COMPLETED [{program_name}]")


# ---


# DO NOT REMOVE PARAMETER: `execution_style`
def func_xss(program_name, domain_list, execution_style):
    func_xss_run(program_name, domain_list)
