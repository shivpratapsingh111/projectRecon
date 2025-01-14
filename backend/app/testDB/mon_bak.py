# monitor.py
from db_manager import DatabaseManager
from db_operations import DatabaseOperations
import requests
import hashlib
import os
import time
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import Json
import mimetypes
from urllib.parse import urlparse
# from app.config.config import *

root_Data_Dir = "~/projectRecon-Data/"
root_Data_Dir = os.path.expanduser(root_Data_Dir).rstrip('/') # Getting Absolute path
filepath = None

class EndpointMonitor:
    def __init__(self, db_config: dict, urls_file: str, check_interval: int, response_dir: str):
        self.urls_file = urls_file
        self.check_interval = check_interval
        self.response_dir = response_dir
        
        # Initialize database operations
        db_manager = DatabaseManager(db_config)
        self.db_ops = DatabaseOperations(db_manager)
        
        logging.basicConfig(
            level=logging.DEBUG,  # Set logging level to DEBUG
            format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            handlers=[
                logging.FileHandler('endpoint_monitor.log', mode='a'),  # Append mode for the log file
                logging.StreamHandler()  # Print logs to the terminal
            ]
        )
        
        # Create a logger for the class
        self.logger = logging.getLogger(self.__class__.__name__)  # Use the class name for better context
        self.logger.setLevel(logging.DEBUG)  # Ensure the logger level is set to DEBUG

        os.makedirs(response_dir, exist_ok=True)

    def sanitize_url(self, url):
        parsed_url = urlparse(url)
        clean_url = parsed_url.netloc + parsed_url.path  # Remove protocol
        return clean_url.replace("/", "_")  # Replace '/' with '_'


    def check_endpoint(self, url: str):
        """Check a single endpoint and record changes"""
        global filepath
        try:
            # Make the request
            response = requests.get(url, stream=True, timeout=30)
            self.logger.info(f"URL: {response.text}")
            
            content_type = response.headers.get('Content-Type', '')
            ext = mimetypes.guess_extension(content_type.split(";")[0]) or ".bin"  # Guess file extension
            result_dir = f"{root_Data_Dir}/monitoring"
            os.makedirs(result_dir, exist_ok=True)
            filename = f"{self.sanitize_url(url)}{ext}"
            filepath = f"{result_dir}/{filename}"
            
            if not os.path.exists(filepath) and not os.path.exists(f"{filepath}_new"):
                print(f"1st time - Neither new file nor old file found")
            
                if "text" in content_type or "json" in content_type:
                    with open(filepath, "w", encoding="utf-8") as file:
                        file.write(response.text)  # Save as text
                else:
                    with open(filepath, "wb") as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)  # Save as binary
            elif os.path.exists(filepath) and not os.path.exists(f"{filepath}_new"):
                print(f"2nd time - No new file, only old one")
                filepath = f"{filepath}_new"
            
                if "text" in content_type or "json" in content_type:
                    with open(filepath, "w", encoding="utf-8") as file:
                        file.write(response.text)  # Save as text
                else:
                    with open(filepath, "wb") as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)  # Save as binary
            elif os.path.exists(filepath) and os.path.exists(f"{filepath}_new"):
                print(f"Moving  new to old and creating new")
                os.rename(f"{filepath}_new", filepath)
                filepath = f"{filepath}_new"
            
                if "text" in content_type or "json" in content_type:
                    with open(filepath, "w", encoding="utf-8") as file:
                        file.write(response.text)  # Save as text
                else:
                    with open(filepath, "wb") as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)  # Save as binary

            
            
            # Calculate current response data
            current_data = {
                'url': url,
                'old_status_code': None,
                'new_status_code': response.status_code,
                'old_response_size': None,
                'new_response_size': len(response.content),
                'old_body_hash': None,
                'new_body_hash': hashlib.sha256(response.text.encode()).hexdigest(),
                'old_body_file_path': None,
                'new_body_file_path': filepath
                }
            
            # Get previous data
            previous_data = self.db_ops.query_operations().get_endpoint_data_by_url(url)
            
            try:
                if previous_data:
                    # Compare and record changes if needed
                    changes = self._detect_changes(previous_data, current_data)
                    if changes:
                        self.logger.info(f"Changes detected for {url}")
                        self.db_ops.update_operations().update_endpoint_data(previous_data['id'], changes)
                        self.logger.info(f"Updated in DB")
                    else:
                        self.logger.info(f"No Changes detected for {url}")
                        
                else:
                    # First time seeing this endpoint
                    try:
                        endpoint_id = self.db_ops.insert_operations().insert_endpoint(current_data)
                        self.logger.info(f"[Success] New Endpoint added to DB: {url}")
                    except Exception as e:
                        logging.exception("Error")
                        self.logger.error(f"Unable to add endpoint to DB: {url} - {str(e)}")
                                            
            except Exception as e:
                logging.exception("Error")
                self.logger.error(f"Something went wrong while collecting data for new endpoint :{url} - {str(e)}")                
        except Exception as e:
            logging.exception("Error")
            self.logger.error(f"Error checking: {url} - {str(e)}")

    def _detect_changes(self, previous_data: dict, current_data: dict) -> dict:
        """Detect changes between two responses"""
        changes_detected = []
        
        # current_data['old_response_size'] = previous_data.get('new_response_size')
        # current_data['old_status_code'] = previous_data.get('new_status_code')

        print(f" [Status Code] Previous: {previous_data.get('new_status_code')} Current: {current_data.get('new_status_code')}")
        print(f" [Response Size] Previous: {previous_data.get('new_response_size')} Current: {current_data.get('new_response_size')}")
        print(f" [Body Hash] Previous: {previous_data.get('new_body_hash')} Current: {current_data.get('new_body_hash')}")
        print(f" [File Path] Previous: {previous_data.get('new_body_file_path')} Current: {current_data.get('new_body_file_path')}")


        if previous_data.get('new_status_code') != current_data.get('new_status_code'):
            changes_detected.append("status_code")
            current_data['old_status_code'] = previous_data.get('new_status_code')
    
        if previous_data.get('new_response_size') != current_data.get('new_response_size'):
            changes_detected.append("response_size")
            current_data['old_response_size'] = previous_data.get('new_response_size')

        
        if previous_data.get('new_body_hash') != current_data.get('new_body_hash'):
            changes_detected.append("body_hash")
            current_data['old_body_hash'] = previous_data.get('new_body_hash')
        
            current_data['old_response_size'] = previous_data.get('new_response_size')
        
        if previous_data.get('new_body_file_path') != current_data.get('new_body_file_path'):
            changes_detected.append("body_file_path")
            current_data['old_body_file_path'] = previous_data.get('new_body_file_path')

            current_data['old_response_size'] = previous_data.get('new_response_size')
        
        print(f"Changes detected: {changes_detected}")
        return current_data

    def run(self):
        """Main monitoring loop"""
        self.logger.info(f"Starting endpoint monitoring every {self.check_interval} seconds")
        
        while True:
            with open(self.urls_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
                
            for url in urls:
                try:
                    self.logger.info(f"Requesting URL: {url}")
                    self.check_endpoint(url)
                except Exception as e:
                    logging.exception("Error")
                    self.logger.error(f"Failed to check {url}: {str(e)}")
            
            time.sleep(self.check_interval)

if __name__ == "__main__":
    db_config = {
        'dbname': 'test_monitor',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost'
    }
    
    monitor = EndpointMonitor(
        db_config=db_config,
        urls_file='endpoints.txt',
        check_interval=10,  # run on every 10 seconds
        response_dir='responses'
    )
    
    monitor.run()