from concurrent.futures import ThreadPoolExecutor
import subprocess, os
from app.config.config  import *



from concurrent.futures import ThreadPoolExecutor, Future
import subprocess
import os
from app.config.config import *

# Global dictionary to track processes and their statuses
processes = {}  # Format: {"tool_name": {"process": process_obj, "status": "running/completed/failed", "stdout_file": "path", "stderr_file": "path", "future": future_obj}}

# Initialize the ThreadPoolExecutor outside the functions for reuse
executor = ThreadPoolExecutor(max_workers=5)

# File paths
stdout_file = "stdout.log"
stderr_file = "stderr.log"

def start_tool(target_name, tool_name, command, file_name):
    """
    Start a tool/script, redirect its output to a log file, and update the process registry.
    """
    global processes, stdout_file, stderr_file
    stdout_file = file_name
    stderr_file = f"{root_Data_Dir}/{target_name}/logs/stderr_{tool_name}.log"
    with open(stdout_file, "w") as output, open(stderr_file, "a") as stderr_log:
        process = subprocess.Popen(
            command,
            stdout=output,         # Redirect stdout to stdout_file
            stderr=stderr_log,     # Redirect stderr to stderr_file
            shell=True,
            preexec_fn=os.setsid   # Start the process in a new process group
        )
    processes[tool_name] = {"process": process, "status": "running", "stdout_file": stdout_file, "stderr_file": stderr_file}
    future = executor.submit(monitor_process, tool_name, target_name)
    processes[tool_name]["future"] = future
    print(f"{tool_name} started with PID: {process.pid}")
    process.wait()
def monitor_process(tool_name, target_name):
    """
    Monitor a process and update its status when it completes.
    """
    global processes
    process = processes[tool_name]["process"]
    process.wait()  # Wait for the process to complete
    exit_code = process.returncode
    if exit_code == 0:
        processes[tool_name]["status"] = "completed"
    else:
        processes[tool_name]["status"] = f"Failed with Exit Code: {exit_code}"

    # Logging process completion status
    try:
        with open(f"{root_Data_Dir}/{target_name}/{central_log_file}", 'a') as f:
            f.write(f"{tool_name} finished with status: {processes[tool_name]['status']}\n")
        print(f"Logged status for {tool_name}")  # Debug print to confirm logging happens
    except Exception as e:
        print(f"Error while writing to log.txt: {e}")

def stop_tool(tool_name):
    """
    Stop a running tool by sending SIGTERM.
    """
    global processes
    process = processes.get(tool_name, {}).get("process")
    if process and process.poll() is None:  # Process is still running
        os.killpg(os.getpgid(process.pid), 15)  # Send SIGTERM to process group
        processes[tool_name]["status"] = "stopped"
        print(f"{tool_name} stopped successfully.")
    else:
        print(f"{tool_name} is not running or does not exist.")

def get_status():
    """
    Return the current status of all tools.
    """
    global processes
    return {tool_name: data["status"] for tool_name, data in processes.items()}

# Example usage
# if __name__ == "__main__":
#     target_name = "example_target"
#     result_dir = "/path/to/result"
#     domain = "example.com"

#     with ThreadPoolExecutor(max_workers=3) as executor:
#         futures = [
#             executor.submit(start_tool, target_name, "assetfinder", f"echo {domain} | assetfinder", f"{result_dir}/assetfinder_output.log"),
#             executor.submit(start_tool, target_name, "subfinder", f"echo {domain} | subfinder", f"{result_dir}/subfinder_output.log"),
#             executor.submit(start_tool, target_name, "subdominator", f"subdominator -d {domain}", f"{result_dir}/subdominator_output.log"),
#         ]

#         # Optionally, wait for all futures to complete
#         for future in futures:
#             future.result()

#     # Print the status of all tools
#     print(get_status())










































# # Global dictionary to track processes and their statuses
# processes = {}  # Format: {"tool_name": {"process": process_obj, "status": "running/completed/failed", "stdout_file": "path", "stderr_file": "path"}}

# # Initialize the ThreadPoolExecutor outside the functions for reuse
# executor = ThreadPoolExecutor(max_workers=5)

# # File paths
# stdout_file = "stdout.log"
# stderr_file = "stderr.log"

# def start_tool(target_name, tool_name, command, file_name):
#     """
#     Start a tool/script, redirect its output to a log file, and update the process registry.
#     """
#     global processes, stdout_file, stderr_file
#     stdout_file = file_name
#     stderr_file = f"{root_Data_Dir}/{target_name}/logs/stderr_{tool_name}.log"
#     with open(stdout_file, "w") as output, open(stderr_file, "a") as stderr_log:
#         process = subprocess.Popen(
#             command,
#             stdout=output,         # Redirect stdout to stdout_file
#             stderr=stderr_log,         # Redirect stderr to stderr_file
#             shell=True,
#             preexec_fn=os.setsid    # Start the process in a new process group
#         )
#     processes[tool_name] = {"process": process, "status": "running", "stdout_file": output, "stderr_file": stderr_log}
#     # Submit the monitoring task to the thread pool
#     executor.submit(monitor_process, tool_name, target_name)
#     print(f"{tool_name} started with PID: {process.pid}")
#     process.wait()

# def monitor_process(tool_name, target_name):
#     """
#     Monitor a process and update its status when it completes.
#     """
#     global processes
#     process = processes[tool_name]["process"]
#     process.wait()  # Wait for the process to complete
#     exit_code = process.returncode
#     if exit_code == 0:
#         processes[tool_name]["status"] = "completed"
#     else:
#         processes[tool_name]["status"] = f"Failed with Exit Code: {exit_code}"

#     # Logging process completion status
#     try:
#         with open(f"{root_Data_Dir}/{target_name}/{central_log_file}", 'a') as f:
#             f.write(f"{tool_name} finished with status: {processes[tool_name]['status']}\n")
#         print(f"Logged status for {tool_name}")  # Debug print to confirm logging happens
#     except Exception as e:
#         print(f"Error while writing to log.txt: {e}")

# def stop_tool(tool_name):
#     """
#     Stop a running tool by sending SIGTERM.
#     """
#     global processes
#     process = processes.get(tool_name, {}).get("process")
#     if process and process.poll() is None:  # Process is still running
#         os.killpg(os.getpgid(process.pid), 15)  # Send SIGTERM to process group
#         processes[tool_name]["status"] = "stopped"
#         print(f"{tool_name} stopped successfully.")
#     else:
#         print(f"{tool_name} is not running or does not exist.")

# def get_status():
#     """
#     Return the current status of all tools.
#     """
#     global processes
#     return processes





















































# import time

# def testss():
#     for i in range(1, 90):  # Goes from 1 to 4
#         print(f"Second: {i}")
#         time.sleep(1)

# def tests():
#     # Use a new ThreadPoolExecutor inside `tests()` to properly manage threads
#     with ThreadPoolExecutor(max_workers=3) as inner_executor:
#         futures = [inner_executor.submit(testss)]
#         # Wait for all submitted tasks to complete
#         for future in futures:
#             future.result()  # Ensures the task is completed

# if __name__ == "__main__":
#     # Start tools using the optimized start_tool
#     start_tool("example1", "ping -c 5 google.com", "example1.log")
#     start_tool("example2", "ping -c 3 yahoo.com", "example2.log")
    
#     # Print status
#     import time
#     time.sleep(2)  # Allow processes to run a bit
#     print("Status:", get_status())

#     # Stop a tool
#     stop_tool("example1")
#     print("After stopping example1:", get_status())

#     # Wait for processes to complete
#     time.sleep(6)
#     print("Final Status:", get_status())
