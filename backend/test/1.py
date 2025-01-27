# from backend.app.interface.json_data_manager import GroupManager
# from app.config.config import *
# data_manager_obj = GroupManager(data_file)

# import json
# with open('groups.json') as f:
#     data = json.load(f)

# for group_uuid in data['groups']:
#     print(group_uuid)

# # print(data_manager_obj._read_file())
# import backend.app.services.scans.arrange_urls
# # Get the file path of the module
# module_path = backend.app.services.scans.arrange_urls.__file__

# print(f"python3 {module_path}")

# from app.interface.process_manager import CommandExecutor

# a= CommandExecutor()

# a._update_process_status(544429, "killed")

import aiohttp
import asyncio
import ssl

# Function to create and configure a session
async def create_session():
    timeout = aiohttp.ClientTimeout(total=5)  # Set timeout to 5 seconds

    # Disable SSL verification
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    session = aiohttp.ClientSession(timeout=timeout, connector=aiohttp.TCPConnector(ssl=ssl_context))
    return session

# Function to make a request using the provided session
async def fetch_data(session, url):
    try:
        async with session.get(url) as response:
            return await response.text()
    except asyncio.TimeoutError:
        return "Request timed out"
    except aiohttp.ClientError as e:
        return f"Request failed: {e}"

# Main function to run everything
async def main():
    url = "http://ftp.halecountryclub.co.uk/"  # Example of an SSL site with self-signed certs
    
    session = await create_session()  # Create the session once
    try:
        response = await fetch_data(session, url)
        print(response)
    finally:
        await session.close()  # Always close the session when done

asyncio.run(main())









# from test_data_manager import GroupManager
# data_manager_obj = GroupManager('groups.json')
# group_name = "intigriti"
# domain = "indeedflexx.com"
# domain_uuid = "75a011e3-1e89-4656-bb1b-b13edb15789e"

# command_details = {
#     "command_name": "htssstpx",
#     "pid": 5,
#     "command": "python server.py",
#     "status": "runssssssssssning",
#     "start_time": "2024-01-15T10:00:00Z"
# }

# pid = 1
# status = "2222222222222222"

# data_manager_obj.update_command_status_by_pid(pid, status)