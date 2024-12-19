from concurrent.futures import ThreadPoolExecutor
from pyscripts.process_manager import start_tool
from app.config.config  import *
import subprocess, asyncio

import subprocess
import multiprocessing
import os
import signal
import psutil
import time
from datetime import datetime

# Logging function
def log_message(log_file, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

# Function to execute a command
def execute_command(command, stdout_file, stderr_file, log_file):
    log_message(log_file, f"Starting command: {command}")
    with open(stdout_file, 'w') as out, open(stderr_file, 'w') as err:
        process = subprocess.Popen(command, shell=True, stdout=out, stderr=err, preexec_fn=os.setsid)
        try:
            process.wait()
            if process.returncode == 0:
                log_message(log_file, f"Command completed successfully: {command}")
            else:
                log_message(log_file, f"Command failed with return code {process.returncode}: {command}")
        except Exception as e:
            log_message(log_file, f"Error while running command: {command}. Error: {str(e)}")
        finally:
            return process.pid

# Monitoring function
def monitor_command(pid):
    try:
        process = psutil.Process(pid)
        status = process.status()
        cpu = process.cpu_percent(interval=1)
        memory = process.memory_info().rss / (1024 * 1024)  # Memory in MB
        return {
            "status": status,
            "cpu_percent": cpu,
            "memory_mb": memory
        }
    except psutil.NoSuchProcess:
        return {
            "status": "not_found",
            "cpu_percent": 0,
            "memory_mb": 0
        }

# Function to stop a specific command
def stop_command(pid, log_file):
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        log_message(log_file, f"Command with PID {pid} terminated.")
    except ProcessLookupError:
        log_message(log_file, f"Command with PID {pid} not found or already terminated.")

# Function to stop all commands
def stop_all(pids, log_file):
    for pid in pids:
        stop_command(pid, log_file)

# Main function
def main():
    group_name = "my_command_group"
    commands = [
        "sleep 1 && echo done",
        "sleep 2 && echo done",
        "sleep 3 && echo done"
    ]
    log_file = f"{group_name}_log.txt"
    processes = []
    pids = []

    # Start commands in parallel
    for i, command in enumerate(commands):
        stdout_file = f"{group_name}_command_{i+1}_stdout.txt"
        stderr_file = f"{group_name}_command_{i+1}_stderr.txt"
        process = multiprocessing.Process(target=execute_command, args=(command, stdout_file, stderr_file, log_file))
        process.start()
        processes.append(process)
        pids.append(process.pid)

    # Wait for all processes to complete
    for process in processes:
        process.join()

    # Monitor resource usage
    for pid in pids:
        status = monitor_command(pid)
        log_message(log_file, f"Monitoring PID {pid}: {status}")

    # Stop all commands if needed
    stop_all(pids, log_file)

if __name__ == "__main__":
    main()



















# print(puredns_ResolversFile)
# print(root_Data_Dir)
# print(temp_Active_SubdomainResults_Path)
# print(temp_Passive_SubdomainResults_Path)
# print(temp_SubdomainResults_Path)

# command='httpx -l asdsad'
# log='HTTPXout.log'
# log1='HTTPXerr.log'
# with open(log, "w") as writeLog:
#     process = subprocess.Popen(
#         command,
#         stdout=writeLog,
#         stderr=writeLog,
#         shell=True,
#     )

# with ThreadPoolExecutor(max_workers=3) as executor:
#     futures = [
#         executor.submit(start_tool, "Assetfinder", "ping -c 5 google.com"),
#         executor.submit(start_tool, "Subfinder", "ping -c 5 youtube.com"),
#         executor.submit(start_tool, "Subdominator", "ping -c 5 youtube.com"),
#         executor.submit(start_tool, "Amass", "ping -c 5 youtube.com")
#     ]
#     # Ensure all tasks in the first set are completed
#     for future in futures:
#         future.result()
# print("First set complete")



# domain_list = ['example.com', 'google.com', 'youtube.com', 'apple.com', 'tests.com']
# target_name = "Mixed"
# # domain = 'tests.com'

# passive_CombinedSubdomainResults = 'a.txt'


# for domain in domain_list:
#     command = f"""cat {passive_CombinedSubdomainResults} | awk '{{print $1}}' | awk '{{print tolower($0)}}' | grep -iE "^(.*\\.)?{domain}$" | sed 's/^[^a-zA-Z0-9]*//' | sed -E 's#^https?://##; s#^www*\\.##' """ # Combining passive results
#     with open(central_log_file , "w") as writeLog:
#         process = subprocess.Popen(
#             command,
#             # stdout=writeLog,
#             stderr=writeLog,
#             shell=True,
#         )

# print(root_Data_Dir)

# async def get_data():
#     sleep(3)
#     return "Data loaded"

# async def maina():
#     result = await get_data()
#     print(result)

# a =asyncio.create_task(maina())
# await a