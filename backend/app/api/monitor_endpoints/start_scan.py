import asyncio
from app.services.monitor_endpoints.db.db_manager import DatabaseManager
from app.services.monitor_endpoints.db.db_operations import DatabaseOperations
from backend.app.services.monitor_endpoints.service_monitor import monitor_endpoints
from collections import defaultdict
import requests

from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='monitor_endpoints', enable_debug = False)

db_config = {
    'dbname': 'test_monitor',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost'
}

db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

# Shared flag to control task execution
scan_status = False

def send_telegram_message(message: str):
    url = 
    payload = {
        ,
        'text': message
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        logger.info("Message sent successfully")
    else:
        logger.exception(f"Failed to send message: {response.status_code}")

def get_endpoints_by_status(status):
    try:
        data = db_ops.query_operations().get_endpoints_data_by_status(status)
        result = []

        if data is not None:
            for row in data:
                entry = {
                    'id': row[0],
                    'program_id': row[1],
                    'program_name': None,
                    'scan_name': row[2],
                    'scan_interval': row[3],
                    'status': row[4],
                    'url': row[5],
                    'new_status_code': row[6],
                    'new_response_size': row[7],
                    'new_body_file_path': row[8],
                    'last_check': str(row[9])
                }

                program_name = db_ops.query_operations().get_program_name(row[1])
                if program_name:
                    entry['program_name'] = program_name[0][0]
                else:
                    entry['program_name'] = None
                result.append(entry)

            return result
        else:
            return None

    except Exception as e:
        logger.exception(f"Error fetching endpoints by status: {e}")
        return None

def group_urls_by_scan_name(endpoints):
    grouped = defaultdict(list)

    for endpoint in endpoints:
        scan_name = endpoint['scan_name']
        grouped[scan_name].append({
            'url': endpoint['url'],
            'scan_interval': endpoint['scan_interval'],
            'last_check': endpoint['last_check']
        })

    return grouped

async def start_scan_for_group(scan_name, urls):
    url_strings = [entry['url'] for entry in urls]
    await monitor_endpoints(url_strings, scan_name)

async def schedule_scans():
    active_endpoints = get_endpoints_by_status("active")

    if active_endpoints:
        grouped_endpoints = group_urls_by_scan_name(active_endpoints)

        for scan_name, urls in grouped_endpoints.items():
            await start_scan_for_group(scan_name, urls)
            # send_telegram_message(f"Scan completed [{scan_name}] Count [{len(urls)}]")
    else:
        logger.warning("No Active endpoints found for scan")
        send_telegram_message("No Active endpoints found for scan")

async def run_periodic_scans():
    logger.info("In periodic Scan funtion")
    global scan_status

    scan_status = True

    while scan_status:
        logger.info("Starting scheduled scans...")
        await schedule_scans()
        logger.info("Scheduled scans completed. Waiting for the next interval...")
        await asyncio.sleep(5)  # 4 hours interval
    logger.info(f"Scan Satus {scan_status}")
    return

async def stop_scans():
    global scan_status
    scan_status = False
    logger.info("Scheduled scans stopped...")
    return {"message": "Stopping scheduled scans..."}

async def get_scan_state():
    global scan_status
    return scan_status

# To start the scans, call run_periodic_scans in an asyncio event loop
# To stop the scans, call stop_scans
