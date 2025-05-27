# External Imports
from collections import defaultdict
import urllib.parse
import urllib.request
import asyncio

# Local Imports
from app.config.db_config import db_config
from app.services.monitor_endpoints.db.db_manager import DatabaseManager
from app.services.monitor_endpoints.db.db_operations import DatabaseOperations
from app.services.monitor_endpoints.service_monitor import monitor_endpoints
from app.logger.logger import setup_logger
from app.config.config import(
    TELEGRAM_WEBHOOK, 
	TELEGRAM_CHAT_ID,
	MONITOR_SCANS_PERIOD
)

# Initialization
logger = setup_logger(__name__, log_file_path='monitor_endpoints', enable_debug = True)
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

scan_status = False # Shared flag to control task execution

# Logic
async def send_telegram_message(message: str):
    logger.debug(f"Notifying on Telegram: {message}")
    url = TELEGRAM_WEBHOOK
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    data = urllib.parse.urlencode(payload).encode()
    try:
        response = await asyncio.to_thread(make_request, url, data)
        if response.status == 200:
            logger.info("Message sent successfully")
        else:
            logger.exception(f"Failed to send message: {response.status}")
        logger.debug("Notification sent on Telegram")
    except Exception as e:
        logger.exception(f"Error sending message: {e}")
    logger.debug("Done with Notification")

# ---

def make_request(url, data):
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=1) as response:
            return response
    except urllib.error.URLError as e:
        logger.exception(f"Error in urllib request: {e}")
        raise
    
# ---
    
def get_endpoints_by_status(status):
    try:
        data = db_ops.query_operations().get_endpoints_data_by_status(status)
        result = []
        if data is not None:
            for row in data:
                entry = {
                    'id': row[0],
                    'program_uuid': row[1],
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

# ---

def groupby_urls_by_scan_name(endpoints):
    grouped = defaultdict(list)
    for endpoint in endpoints:
        scan_name = endpoint['scan_name']
        grouped[scan_name].append({
            'url': endpoint['url'],
            'scan_interval': endpoint['scan_interval'],
            'last_check': endpoint['last_check']
        })
    return grouped

# ---

async def start_scan_for_group(scan_name, urls):
    url_strings = [entry['url'] for entry in urls]
    result = await monitor_endpoints(url_strings, scan_name)
    logger.debug(f"Got result {result}")
    return result

# ---

async def schedule_scans():
    active_endpoints = get_endpoints_by_status("active")
    logger.debug(f"Got {len(active_endpoints)} active endpoints.")
    if active_endpoints:
        grouped_endpoints = groupby_urls_by_scan_name(active_endpoints)
        for scan_name, urls in grouped_endpoints.items():
            result = await start_scan_for_group(scan_name, urls)
            logger.debug(f"Got result {result}")
            await send_telegram_message(f"Scan completed [{scan_name}] Count [{len(urls)}]")
        return "Done with scheduled scans"
    else:
        logger.warning("No Active endpoints found for scan")
        await send_telegram_message("No Active endpoints found for scan")

# ---

async def start_periodic_monitoring_scans():
    logger.info("In periodic Scan funtion")
    global scan_status
    scan_status = True # UPDATE Global Variable
    while scan_status:
        logger.info("Starting scheduled scans...")
        result = await schedule_scans()
        logger.debug(result)
        logger.info("Scheduled scans completed. Waiting for the next interval...")
        await asyncio.sleep(MONITOR_SCANS_PERIOD)
    logger.info(f"Scan Satus {scan_status}")
    return

# ---

async def stop_periodic_monitoring_scans():
    global scan_status
    scan_status = False
    logger.info("Scheduled scans stopped...")
    return {"message": "Stopping scheduled scans..."}

# ---

async def get_scan_state():
    global scan_status
    return scan_status

# ---

# To start the periodic monitoring scan, call start_periodic_monitoring_scans in an asyncio event loop
# To stop the periodic monitoring scan, call stop_periodic_monitoring_scans
