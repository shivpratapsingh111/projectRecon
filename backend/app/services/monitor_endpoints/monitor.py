# monitor.py
import mimetypes
import aiohttp
import asyncio
import hashlib
import hashlib
import random
import pytz
import ssl
import os

from urllib.parse import urlparse
from datetime import datetime
from psycopg2.extras import Json
from urllib.parse import urlparse
from asyncio import Queue
from aiohttp import ClientSession, ClientTimeout
from datetime import datetime
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from aiohttp.client_exceptions import ClientConnectionError
from app.services.monitor_endpoints.logger import setup_logger

from app.db.db_manager import DatabaseManager
from app.db.db_operations import DatabaseOperations


# ------------------------------------ Constants ---------------------------------------#|
ROOT_DATA_DIR = "~/projectRecon-Data/"                                                  #|
ROOT_DATA_DIR = os.path.expanduser(ROOT_DATA_DIR).rstrip('/') # Getting Absolute path   #|
MAX_CONCURRENT_REQUESTS = 10                                                            #|
MAX_RETRIES = 3                                                                         #|
RETRY_BACKOFF = 2                                                                       #|
TIMEOUT = 10                                                                            #|
                                                                                        #|
filepath = None                                                                         #|  
# ------------------------------------ Constants ---------------------------------------#|

@dataclass
class ChangeMetadata:
    field_name: str
    old_value: any
    new_value: any

class EndpointChangeDetector:
    def __init__(self, db_ops):
        self.db_ops = db_ops
    
    def detect_and_update_changes(self, previous_data: Dict, current_data: Dict) -> Tuple[bool, List[str]]:
        """
        Detects changes between previous and current endpoint data and updates the database accordingly.
        Returns a tuple of (changes_detected: bool, changed_fields: List[str])
        """
        changes: List[ChangeMetadata] = []
        changed_fields: List[str] = []
        
        # Fields to compare and their corresponding old/new field names
        fields_to_check = {
            'status_code': ('old_status_code', 'new_status_code'),
            'response_size': ('old_response_size', 'new_response_size'),
            'body_hash': ('old_body_hash', 'new_body_hash'),
            'body_file_path': ('old_body_file_path', 'new_body_file_path')
        }
                
        for field, (old_field, new_field) in fields_to_check.items():
            prev_value = previous_data.get(new_field)  # Get the previous "new" value
            prev_value_old = previous_data.get(old_field)  # Get the previous "old" value
            curr_value = current_data.get(new_field)   # Get the current "new" value
            curr_value_old = current_data.get(old_field)   # Get the current "old" value
            
            logger.debug(f"===[DEBUG] - [{field}]===")
            logger.debug(f"prev_value [{new_field}] [new]: {prev_value}")
            logger.debug(f"prev_value [{old_field}] [old]: {prev_value_old}")
            logger.debug(f"curr_value [{new_field}] [new]: {curr_value}")
            logger.debug(f"curr_value [{old_field}] [old]: {curr_value_old}")
            logger.debug("==========================")
            
            if self._is_change(field, prev_value, curr_value):
                changes.append(ChangeMetadata(
                    field_name=field,
                    old_value=prev_value,
                    new_value=curr_value
                ))
                changed_fields.append(field)
            
            logger.debug(f"===[DEBUG] - [{field}]===")
            logger.debug(f"Current Data before update: \n{current_data}")

            current_data[old_field] = prev_value # Update the old value in current_data
            current_data['change_detected_at'] = datetime.now()

            logger.debug(f"Current Data after update: \n{current_data}")
            logger.debug("==========================")
        
        if changes:
            self._update_database(previous_data['id'], current_data, changes)
            return True, changed_fields
        else:
            self.db_ops.update_operations().update_endpoint_timestamp(previous_data['id'])
            logger.debug("Updated timestamp - [NO CHANGES DETECTED]")
        
        return False, []
    
    def _is_change(self, field: str, old_value: any, new_value: any) -> bool:
        """
        Determines if a change is significant enough to warrant an update.
        Implements specific logic for different types of fields.
        """

        if field == 'status_code':
            return old_value != new_value
                            
        elif field == 'body_hash':
            return old_value != new_value
        
        else:            
            return False
    
    def _update_database(self, endpoint_id: str, current_data: Dict, changes: List[ChangeMetadata]) -> None:
        """
        Updates the database with the detected changes and metadata.
        """
        try:
            # Prepare update data
            update_data = {
                **current_data,
                'change_detected_at': datetime.fromtimestamp(1705246731, pytz.timezone("Asia/Kolkata")),
            }

            
            # Log the changes
            change_summary = ", ".join([
                f"{change.field_name}"
                for change in changes
            ])
            
            # Perform the update
            self.db_ops.update_operations().update_endpoint_data(endpoint_id, update_data)
            logger.info(f"[CHANGES DETECTED] [{update_data['url']}] [{change_summary}]")
                            
        except Exception as e:
            logger.exception(f"Failed to update database for endpoint {endpoint_id}: {str(e)}")
            raise

class EndpointMonitor:
    def __init__(self, db_config: dict, urls_file: str, check_interval: int):
        self.urls_file = urls_file
        self.check_interval = check_interval
        
        # Initialize database operations
        db_manager = DatabaseManager(db_config)
        self.db_ops = DatabaseOperations(db_manager)
        
        self.change_detector = EndpointChangeDetector(self.db_ops)

    async def sanitize_url(self, url):
        parsed_url = urlparse(url)
        clean_url = parsed_url.netloc + parsed_url.path  # Remove protocol
        return clean_url.replace("/", "_")  # Replace '/' with '_'

    # Retry logic with exponential backoff
    async def make_request(self, session: ClientSession, url: str, retries: int = MAX_RETRIES):
        logger.debug(f"In [make_request] function for [{url}]")
        attempt = 0
        while attempt < retries:
            logger.debug(f"In [make_request]-[while loop] for [{url}]")
            try:
                logger.debug(f"In [make_request]-[while loop]-[try block] [sending request] for [{url}]")
                response = await session.get(url, timeout=TIMEOUT)
                logger.debug(f"Got response for [{url}]")
                return response
            except (ClientTimeout, ClientConnectionError) as e:
                attempt += 1
                wait_time = RETRY_BACKOFF ** attempt  # Exponential backoff
                logger.warning(f"Error fetching {url}: {str(e)}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            except Exception as e:
                logger.exception(f"Unexpected error fetching {url}: {str(e)}")
                return None
        logger.error(f"Max retries reached for {url}")
        return None


    # Worker to process URLs
    async def worker(self, worker_id: int, url_queue: Queue, session: ClientSession, result_queue: Queue):
        while True:
            url = await url_queue.get()
            if url is None:  # Sentinel value to signal worker shutdown
                break

            logger.debug(f"Worker {worker_id} processing: {url}")
            
            # Fetch the URL with retry logic
            response = await self.make_request(session, url)
            
            if response:
                logger.debug(f"Worker {worker_id} successfully fetched: {url}")
                await result_queue.put((url, response))
            else:
                await result_queue.put((url, "Failed", None))

            url_queue.task_done()  # Mark task as done

    # Result processor to handle the results from workers
    async def process_results(self, result_queue: Queue, scan_name):
        while True:
            result = await result_queue.get()
            logger.debug(f"Got new result from result_queue")
            
            # If the result is None, skip processing and handle it accordingly
            if result is None:
                result_queue.task_done()  # Mark the task as done even if it's None
                logger.debug("Received None from result_queue, Finishing.")
                break
                        
            # Unpack the result tuple (url, status, data)
            url, response = result

            await self.check_endpoint(url, response, scan_name)
                        
            result_queue.task_done()
            logger.debug("All task marked as completed")
                        

    async def check_endpoint(self, url, response, scan_name):
        """Check a single endpoint and record changes"""
        global filepath
        try:
            # Make the request
            response_body = await response.text()
            status_code = response.status
            response_size = response.content_length
            response_headers = response.headers
            body_hash = hashlib.sha256(response_body.encode()).hexdigest()
            
            logger.debug(f"Response Body for [{url}]:\n{response_body}")
            
            content_type = response_headers.get('Content-Type', '')
            ext = mimetypes.guess_extension(content_type.split(";")[0]) or ".bin"  # Guess file extension
            result_dir = f"{ROOT_DATA_DIR}/monitoring/{scan_name}/responses"
            os.makedirs(result_dir, exist_ok=True)
            logger.debug(f"Made monitoring dir {result_dir}")
            sanitezed_filename = await self.sanitize_url(url)
            filename = f"{sanitezed_filename}{ext}"
            filepath = f"{result_dir}/{filename}" # use default file name
            
            # Calculate current response data
            current_data = {
                'url': url,
                'old_status_code': None,
                'new_status_code': status_code,
                'old_response_size': None,
                'new_response_size': response_size,
                'old_body_hash': None,
                'new_body_hash': body_hash,
                'old_body_file_path': None,
                'new_body_file_path': filepath,
                'change_detected_at': None
                }

            # Get previous data
            previous_data = self.db_ops.query_operations().get_endpoint_data_by_url(url)

            if previous_data is not None:
                logger.debug(f"Feteched previous data: {previous_data}")

                if previous_data['new_body_hash'] != current_data['new_body_hash']:
                    logger.debug(f"Response Body changed. New body hash{current_data['new_body_hash']}")
                    
                    if not os.path.exists(filepath) and not os.path.exists(f"{filepath}_new"):
                        logger.debug(f"1st time - Neither new body file, nor old body file found")
                        
                        filepath = f"{result_dir}/{filename}" # use default file name
                        current_data['new_body_file_path'] = filepath # update filename for new_body_filepath
                        
                        if "text" in content_type or "json" in content_type:
                            with open(filepath, "w", encoding="utf-8") as file:
                                file.write(response_body)
                                logger.debug(f"Response Body saved as text file [{filepath}]")
                        else:
                            with open(filepath, "wb") as file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    file.write(chunk)  # Save as binary
                                    logger.debug(f"Response Body saved as binary file [{filepath}]")
                                    
                    elif os.path.exists(filepath) and not os.path.exists(f"{filepath}_new"):
                        logger.debug(f"2nd time - No new body file, old body file exists")
                        
                        current_data['old_body_file_path'] = filepath # update filename for old_body_filepath
                        
                        filepath = f"{filepath}_new" # Use new file to save new response
                        current_data['new_body_file_path'] = filepath # update filename for new_body_filepath
                    
                        if "text" in content_type or "json" in content_type:
                            with open(filepath, "w", encoding="utf-8") as file:
                                file.write(response_body)  # Save as text
                                logger.debug(f"Response Body saved as text file [{filepath}]")
                                
                        else:
                            with open(filepath, "wb") as file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    file.write(chunk)  # Save as binary
                                    logger.debug(f"Response Body saved as binary file [{filepath}]")
                                    
                    elif not os.path.exists(filepath) and os.path.exists(f"{filepath}_new"):
                        logger.debug(f"old body file doesn't exists - Moving new to old and creating new")
                        
                        filepath = f"{result_dir}/{filename}"
                        current_data['old_body_file_path'] = filepath # update filename for old_body_filepath

                        os.rename(f"{filepath}_new", filepath) # rename exisiting new file to old
                        filepath = f"{filepath}_new" # save new data to new file
                        current_data['new_body_file_path'] = filepath # update filename for new_body_filepath
                    
                        if "text" in content_type or "json" in content_type:
                            with open(filepath, "w", encoding="utf-8") as file:
                                file.write(response_body)  # Save as text
                                logger.debug(f"Response Body saved as text file [{filepath}]")
                                
                        else:
                            with open(filepath, "wb") as file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    file.write(chunk)  # Save as binary
                                    logger.debug(f"Response Body saved as binary file [{filepath}]")
                                    

                    elif os.path.exists(filepath) and os.path.exists(f"{filepath}_new"):
                        logger.debug(f"Both file exists - Moving new to old and creating new")
                        
                        filepath = f"{result_dir}/{filename}"
                        current_data['old_body_file_path'] = filepath # update filename for old_body_filepath

                        os.rename(f"{filepath}_new", filepath) # rename exisiting new file to old
                        filepath = f"{filepath}_new" # save new data to new file
                        current_data['new_body_file_path'] = filepath # update filename for new_body_filepath

                        if "text" in content_type or "json" in content_type:
                            with open(filepath, "w", encoding="utf-8") as file:
                                file.write(response_body)  # Save as text
                                logger.debug(f"Response Body saved as text file [{filepath}]")
                                
                        else:
                            with open(filepath, "wb") as file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    file.write(chunk)  # Save as binary
                                    logger.debug(f"Response Body saved as binary file [{filepath}]")

                else:
                    logger.info(f"[NO CHANGES DETECTED] - Same body hash for [{url}]")
                    if not os.path.exists(current_data['new_body_file_path']):
                        logger.warning(f"Old responses not detected, Starting fresh...")
                        
                        filepath = f"{result_dir}/{filename}" # use default file name
                        current_data['new_body_file_path'] = filepath # update filename for new_body_filepath
                        
                        if "text" in content_type or "json" in content_type:
                            with open(filepath, "w", encoding="utf-8") as file:
                                file.write(response_body)
                                logger.debug(f"Response Body saved as text file [{filepath}]")
                        else:
                            with open(filepath, "wb") as file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    file.write(chunk)  # Save as binary
                                    logger.debug(f"Response Body saved as binary file [{filepath}]")

            else:
                logger.debug(f"Previous Data is None, New Endpoint")
                

                if not os.path.exists(filepath) and not os.path.exists(f"{filepath}_new"):
                    logger.debug(f"1st time - Neither new body file, nor old body file found")
                    
                    filepath = f"{result_dir}/{filename}" # use default file name
                    current_data['new_body_file_path'] = filepath # update filename for new_body_filepath
                    
                    if "text" in content_type or "json" in content_type:
                        with open(filepath, "w", encoding="utf-8") as file:
                            file.write(response_body)  # Save as text
                            logger.debug(f"Response Body saved as text file [{filepath}]")
                    else:
                        with open(filepath, "wb") as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)  # Save as binary
                                logger.debug(f"Response Body saved as binary file [{filepath}]")
                                
                elif os.path.exists(filepath) and not os.path.exists(f"{filepath}_new"):
                    logger.debug(f"2nd time - No new body file, old body file exists")
                    
                    current_data['old_body_file_path'] = filepath # update filename for old_body_filepath
                    
                    filepath = f"{filepath}_new" # Use new file to save new response
                    current_data['new_body_file_path'] = filepath # update filename for new_body_filepath
                
                    if "text" in content_type or "json" in content_type:
                        with open(filepath, "w", encoding="utf-8") as file:
                            file.write(response_body)  # Save as text
                            logger.debug(f"Response Body saved as text file [{filepath}]")
                    else:
                        with open(filepath, "wb") as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)  # Save as binary
                                logger.debug(f"Response Body saved as binary file [{filepath}]")
                                
                elif not os.path.exists(filepath) and os.path.exists(f"{filepath}_new"):
                    logger.debug(f"old body file doesn't exists - Moving new to old and creating new")
                    
                    filepath = f"{result_dir}/{filename}"
                    current_data['old_body_file_path'] = filepath # update filename for old_body_filepath
                    os.rename(f"{filepath}_new", filepath) # rename exisiting new file to old
                    filepath = f"{filepath}_new" # save new data to new file
                    current_data['new_body_file_path'] = filepath # update filename for new_body_filepath
                
                    if "text" in content_type or "json" in content_type:
                        with open(filepath, "w", encoding="utf-8") as file:
                            file.write(response_body)  # Save as text
                            logger.debug(f"Response Body saved as text file [{filepath}]")
                    else:
                        with open(filepath, "wb") as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)  # Save as binary
                                logger.debug(f"Response Body saved as binary file [{filepath}]")
                                
                                
                elif os.path.exists(filepath) and os.path.exists(f"{filepath}_new"):
                    logger.debug(f"Both file exists - Moving new to old and creating new")
                    
                    filepath = f"{result_dir}/{filename}"
                    current_data['old_body_file_path'] = filepath # update filename for old_body_filepath
                    os.rename(f"{filepath}_new", filepath) # rename exisiting new file to old
                    filepath = f"{filepath}_new" # save new data to new file
                    current_data['new_body_file_path'] = filepath # update filename for new_body_filepath
                    if "text" in content_type or "json" in content_type:
                        with open(filepath, "w", encoding="utf-8") as file:
                            file.write(response_body)  # Save as text
                            logger.debug(f"Response Body saved as text file [{filepath}]")
                    else:
                        with open(filepath, "wb") as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)  # Save as binary
                                logger.debug(f"Response Body saved as binary file [{filepath}]")
            
            try:
                if previous_data:
                    # Compare and record changes if needed
                    changes = self._detect_changes(previous_data, current_data)
                    if changes:
                        self.db_ops.update_operations().update_endpoint_data(previous_data['id'], changes)
                        logger.debug(f"Changes Updated in DB")
                        
                else:
                    # First time seeing this endpoint
                    try:
                        endpoint_id = self.db_ops.insert_operations().insert_endpoint(current_data)
                        logger.info(f"[Success] New Endpoint added to DB: [{endpoint_id}]-[{url}]")
                    except Exception as e:
                        logger.exception(f"Unable to add endpoint to DB: [{endpoint_id}]-[{url}] - [{str(e)}]")
                                            
            except Exception as e:
                logger.exception(f"Something went wrong while collecting data for new endpoint [{url}] - [{str(e)}]")                
        except Exception as e:
            logger.exception(f"Error checking: [{url}] - [{str(e)}]")

    def _detect_changes(self, previous_data: dict, current_data: dict) -> dict:
        changes_detected, changed_fields = self.change_detector.detect_and_update_changes(
            previous_data, current_data
        )
        return current_data if changes_detected else {}

    async def generate_random_headers(self):
        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0",
            "Mozilla/5.0 (Linux; Android 9; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36"
        ]
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        return headers


    async def is_valid_http_url(self, url: str) -> bool:
        parsed_url = urlparse(url)
        return parsed_url.scheme in ["http", "https"] and bool(parsed_url.netloc)


    async def run(self, urls, scan_name):
        """Main monitoring loop"""
        headers = await self.generate_random_headers()
        
        logger.debug(f"[Headers]: {headers}")
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(ssl=ssl_context)
        url_queue = asyncio.Queue()
        result_queue = asyncio.Queue()
        workers = []
        # with open(self.urls_file, 'r') as f:
        #     logger.debug(f"Opened [{self.urls_file}] to read urls")
        #     urls = [line.strip() for line in f if line.strip()]
        for url in urls:
            if await self.is_valid_http_url(url):
                await url_queue.put(url)
            else:
                logger.warning(f"[Not a URL] [{url}]")
        url_queue_count = url_queue.qsize()
        logger.info(f"Endpoints [Count: {url_queue_count}]")
            
        try:
            async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
                # Start workers
                for worker_id in range(MAX_CONCURRENT_REQUESTS):
                    workers.append(asyncio.create_task(self.worker(worker_id, url_queue, session, result_queue)))
                    
                result_processor = asyncio.create_task(self.process_results(result_queue, scan_name))
                await url_queue.join()
                
                # Stop workers gracefully by putting None in the url_queue
                for _ in range(MAX_CONCURRENT_REQUESTS):
                    await url_queue.put(None)
                # Wait for all workers to finish
                await asyncio.gather(*workers)
                # Stop result processor gracefully
                await result_queue.put(None)
                await result_processor
                
                logger.info(f"Completed [Count: {url_queue_count}]")
        except Exception as e:
            logger.exception(f"Failed to pass url_queue to process_urls function [{str(e)}]")
            
    async def monitor_loop(self, urls, scan_name):
        """Monitor loop that keeps running every check_interval seconds"""
        while True:
            print("\n")
            logger.info("=====[START]=====")
            await self.run(urls, scan_name)  # Run the monitoring task
            logger.info("=====[END]=====")
            print("\n")
            logger.info(f"Next scan in {self.check_interval} seconds")
            await asyncio.sleep(self.check_interval)  # Wait for the specified interval

async def monitor_endpoints(urls, scan_name):
    global logger
    db_config = {
        'dbname': 'test_monitor',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost'
    }
    log_dir = f"{ROOT_DATA_DIR}/monitoring/logs"
    os.makedirs(log_dir, exist_ok=True)
    # logger = setup_logger("endpoint_monitor", enable_debug=True)
    logger = setup_logger("endpoint_monitor", enable_debug=False)
    
    monitor = EndpointMonitor(
        db_config=db_config,
        urls_file='endpoints.txt',
        check_interval=10,  # run every 10 seconds
    )

    logger.debug(f"Endpoints Provided [{urls}]")
    await monitor.monitor_loop(urls, scan_name)

    # try:
    #     loop = asyncio.get_running_loop()  # Get the running event loop
    # except RuntimeError:
    #     loop = asyncio.new_event_loop()  # Create a new event loop if none exists
    #     asyncio.set_event_loop(loop)

    # # Schedule the coroutine asynchronously
    # loop.create_task(monitor.monitor_loop(urls, scan_name))

# urls = ['http://0.0.0.0:8080', 'https://www.google.com']
# asyncio.run(monitor_endpoints(urls, "Test-Scan"))