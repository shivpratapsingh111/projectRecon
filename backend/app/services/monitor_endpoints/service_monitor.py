    
from .change_detector import EndpointChangeDetector
from app.services.monitor_endpoints.db.db_manager import DatabaseManager
from app.services.monitor_endpoints.db.db_operations import DatabaseOperations
from app.config.db_config import db_config

from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='monitor_endpoints', enable_debug = False)


from aiohttp import ClientSession, ClientTimeout, ClientConnectorError, ClientOSError, ServerTimeoutError, ClientSSLError
from aiohttp import ClientSession, ClientTimeout
from urllib.parse import urlparse
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict, Any
import mimetypes
import aiohttp
import asyncio
import hashlib
import socket
import random
import ssl
import os

@dataclass
class ChangeMetadata:
    field_name: str
    old_value: any
    new_value: any

# Constants
ROOT_DATA_DIR = os.path.expanduser("~/projectRecon-Data/").rstrip('/')
MAX_CONCURRENT_REQUESTS = 10
MAX_RETRIES = 3
RETRY_BACKOFF = 2
TIMEOUT = 3

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0",
    "Mozilla/5.0 (Linux; Android 9; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36"
]

@dataclass
class ChangeMetadata:
    field_name: str
    old_value: Any
    new_value: Any

@dataclass
class ResponseData:
    url: str
    body: str
    status_code: int
    content_length: Optional[int]
    headers: Dict[str, str]
    content_type: str

class FileManager:
    def __init__(self, root_dir: str, scan_name: str):
        self.result_dir = f"{root_dir}/monitoring/{scan_name}/responses"
        os.makedirs(self.result_dir, exist_ok=True)

    async def sanitize_filename(self, url: str) -> str:
        parsed_url = urlparse(url)
        clean_url = parsed_url.netloc + parsed_url.path
        return clean_url.replace("/", "_")

    async def save_response(self, response_data: ResponseData) -> Tuple[str, str]:
        sanitized_filename = await self.sanitize_filename(response_data.url)
        ext = mimetypes.guess_extension(response_data.content_type.split(";")[0]) or ".bin"
        base_filepath = f"{self.result_dir}/{sanitized_filename}{ext}"
        
        # Determine file paths for old and new content
        old_path = base_filepath
        new_path = f"{base_filepath}_new"
        
        # Handle file rotation
        if os.path.exists(new_path):
            if os.path.exists(old_path):
                os.remove(old_path)
            os.rename(new_path, old_path)
        
        # Save new content
        mode = "w" if "text" in response_data.content_type or "json" in response_data.content_type else "wb"
        content = response_data.body if mode == "w" else response_data.body.encode()
        
        with open(new_path, mode) as file:
            file.write(content)
            logger.debug(f"Response saved to {new_path}")
            
        return old_path, new_path

class EndpointMonitor:
    def __init__(self, db_config: dict, urls_file: str, check_interval: int):
        self.urls_file = urls_file
        self.check_interval = check_interval
        
        self.db_manager = DatabaseManager(db_config)
        self.db_ops = DatabaseOperations(self.db_manager)
        self.change_detector = EndpointChangeDetector(self.db_ops)
        self.file_manager = FileManager(ROOT_DATA_DIR, "")

    async def make_request(self, session: ClientSession, url: str) -> Optional[aiohttp.ClientResponse]:
        for attempt in range(MAX_RETRIES):
            try:
                logger.debug(f"Making request for {url} (Attempt {attempt + 1})")

                # Preemptively resolve the host to catch early DNS failures
                host = url.split("//")[-1].split("/")[0]
                try:
                    ip = socket.gethostbyname(host)
                    logger.debug(f"Resolved {host} to {ip}")
                except socket.gaierror:
                    logger.error(f"DNS resolution failed for {host}")
                    return None
                
                async with session.get(url) as response:
                    logger.debug(f"Got response for {url} with status {response.status}")
                    return await response
                # If the response is received successfully
                return response

            except asyncio.TimeoutError:
                wait_time = min(RETRY_BACKOFF ** attempt, 30)
                logger.warning(f"Timeout fetching {url}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except ServerTimeoutError:
                wait_time = min(RETRY_BACKOFF ** attempt, 30)
                logger.warning(f"Timeout fetching {url}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except ClientTimeout:
                wait_time = min(RETRY_BACKOFF ** attempt, 30)
                logger.warning(f"Timeout fetching {url}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            
            except asyncio.CancelledError:
                logger.error(f"Request to {url} was cancelled, possibly due to shutdown.")
                break  # Handle task cancellation gracefully

            except Exception as e:
                logger.exception(f"Unexpected error fetching {url}: {str(e)}")
                break  # Avoid infinite retries on unknown errors

        logger.error(f"Max retries reached for {url}, request failed.")
        return None


    async def get_program_and_target_id(self, url):
            logger.info(f"Getting Program and Target Id for {url}")
            target_domain = urlparse(url).hostname.lower()
            ids = self.db_ops.query_operations().get_target_and_program_id(target_domain)
            return ids


    async def process_response(self, url: str, response: aiohttp.ClientResponse, scan_name: str) -> None:
        try:
            # Get response content length from headers (if available)
            content_length = response.content_length  

            # If content_length is not available, manually compute response size
            response_body = await response.read()  # Read the body as bytes
            response_size = len(response_body)  # Get response size in bytes
            
            response_data = ResponseData(
                url=url,
                body=response_body.decode(errors="ignore"),  # Decode safely
                status_code=response.status,
                content_length=content_length if content_length else response_size,  # Fallback if None
                headers=dict(response.headers),
                content_type=response.headers.get('Content-Type', '')
            )

            # Save response to file
            old_path, new_path = await self.file_manager.save_response(response_data)

            logger.info(f"Response Size for [{url}] [{response_size} bytes]")

            current_data = {
                'program_id': None,
                'target_id': None,
                'scan_name': scan_name,
                'status': 'active',
                'url': url,
                'old_status_code': None,
                'new_status_code': response_data.status_code,
                'old_response_size': None,
                'new_response_size': response_size,
                'old_body_hash': None,
                'new_body_hash': hashlib.sha256(response_body).hexdigest(),
                'old_body_file_path': old_path,
                'new_body_file_path': new_path,
                'change_detected_at': None,
                'need_review': False
            }

            # Update program and target IDs if available
            ids = await self.get_program_and_target_id(url)
            if ids:
                current_data['target_id'], current_data['program_id'] = ids

            previous_data = self.db_ops.query_operations().get_endpoint_data_by_url(url)
            if previous_data:
                changes = self.change_detector.detect_and_update_changes(previous_data, current_data)
            else:
                logger.info(f"Endpoint was not found on DB, Adding... [{url}]")
                self.db_ops.insert_operations().insert_endpoint(current_data)
                logger.info(f"New endpoint added to DB: {url}")

        except Exception as e:
            logger.exception(f"Error processing response for {url}: {str(e)}")

    async def worker(self, worker_id: int, queue: asyncio.Queue, session: ClientSession, scan_name: str):
        while True:
            url = await queue.get()
            if url is None:
                break

            logger.debug(f"Worker {worker_id} processing: {url}")
            response = await self.make_request(session, url)
            
            if response:
                await self.process_response(url, response, scan_name)
            
            queue.task_done()

    @staticmethod
    def get_ssl_context() -> ssl.SSLContext:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

    @staticmethod
    def generate_headers() -> Dict[str, str]:
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }

    async def run(self, urls: List[str], scan_name: str):
        self.file_manager = FileManager(ROOT_DATA_DIR, scan_name)
        queue = asyncio.Queue()
        
        # Filter and queue valid URLs
        valid_urls = [url for url in urls if urlparse(url).scheme in ["http", "https"] and urlparse(url).netloc]
        for url in valid_urls:
            await queue.put(url)
            
        logger.info(f"Processing {len(valid_urls)} valid endpoints")


        timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        # Disable SSL verification
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with aiohttp.ClientSession(timeout=timeout, connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            workers = [
                asyncio.create_task(self.worker(i, queue, session, scan_name))
                for i in range(MAX_CONCURRENT_REQUESTS)
            ]
            await queue.join()

            # Ensure workers are done and session is properly closed
            for _ in workers:
                await queue.put(None)
            await asyncio.gather(*workers)

async def monitor_endpoints(urls: List[str], scan_name: str):
        
    monitor = EndpointMonitor(
        db_config=db_config,
        urls_file='endpoints.txt',
        check_interval=10,
    )
        
    print("=====[START]=====")
    await monitor.run(urls, scan_name)
    print("=====[END]=====")