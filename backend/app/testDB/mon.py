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

    def check_endpoint(self, url: str):
        """Check a single endpoint and record changes"""
        try:
            # Make the request
            start_time = time.time()
            response = requests.get(url, timeout=30)
            response_time = time.time() - start_time
            self.logger.info(f"URL: {response.text}")
            # Calculate current response data
            current_data = {
                'status_code': response.status_code,
                'response_size': len(response.content),
                'body_hash': hashlib.sha256(response.text.encode()).hexdigest(),
                'response_body': response.text.encode('utf-8'),
                'headers': psycopg2.extras.Json(response.headers),
                'response_time': response_time
            }
            
            # Get previous data
            query_ops = self.db_ops.query_operations()
            previous_data = query_ops.get_endpoint_data(url)
            
            try:
                if previous_data:
                    # Compare and record changes if needed
                    changes = self._detect_changes(previous_data, current_data)
                    if changes:
                        change_data = {
                            'endpoint_id': previous_data['id'],
                            'old_status_code': previous_data['status_code'],
                            'new_status_code': current_data['status_code'],
                            'old_size': previous_data['response_size'],
                            'new_size': current_data['response_size'],
                            'old_body_hash': previous_data['body_hash'],
                            'new_body_hash': current_data['body_hash'],
                            'old_response_body': previous_data['response_body'],
                            'new_response_body': current_data['response_body'],
                            'old_headers': previous_data['headers'],
                            'new_headers': current_data['headers'],
                            'old_response_time': previous_data['response_time'],
                            'new_response_time': current_data['response_time'],
                            'change_type': changes
                        }
                        self.db_ops.insert_operations().record_change(change_data)
                        self.logger.info(f"Changes detected for {url}: {changes}")
                    else:
                        self.logger.info(f"No Changes detected for {url}")
                        
                    # Update endpoint data
                    self.db_ops.update_operations().update_endpoint_data(
                        previous_data['id'], current_data
                    )
                else:
                    # First time seeing this endpoint
                    try:
                        endpoint_id = self.db_ops.insert_operations().add_endpoint(url)
                        self.logger.info(f"[Success] New Endpoint added to DB: {url}")
                    except Exception as e:
                        self.logger.error(f"Unable to add endpoint to DB: {url} - {str(e)}")
                        
                    try:
                        self.db_ops.update_operations().update_endpoint_data(endpoint_id, current_data)
                        self.logger.error(f"[Success] Added data to {url}")
                        # self.logger.debug(f"[Success] New Endpoint Data added to DB: {url}\n\\_Endpoint ID: {endpoint_id}\n\\_Endpoint Data: {current_data}")
                    except Exception as e:
                        self.logger.error(f"Unable to add data to {url}")
                        # self.logger.debug(f"Unable to add endpoint data to DB: {url} - {str(e)} \n\\_Endpoint ID: {endpoint_id}\n\\_Endpoint Data: {current_data}")
                    
            except Exception as e:
                self.logger.error(f"Something went wrong while collecting data for new endpoint :{url} - {str(e)}")                
        except Exception as e:
            self.logger.error(f"Error checking: {url} - {str(e)}")

    def _detect_changes(self, old_data: dict, new_data: dict) -> list[str]:
        """Detect changes between two responses"""
        changes = []
        
        if old_data['status_code'] != new_data['status_code']:
            changes.append('status_code')
        
        if old_data['response_size'] != new_data['response_size']:
            changes.append('response_size')
        
        if old_data['body_hash'] != new_data['body_hash']:
            changes.append('body_content')
            
        if old_data['response_body'] != new_data['response_body']:
            changes.append('response_body')
                        
        # Compare important headers
        important_headers = {'content-type', 'server', 'last-modified', 'etag'}
        old_headers = {k.lower(): v for k, v in old_data['headers'].items()}
        new_headers = {k.lower(): v for k, v in new_data['headers'].items()}
        
        for header in important_headers:
            if old_headers.get(header) != new_headers.get(header):
                changes.append(f'header_{header}')
                
        return changes

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
                    self.logger.error(f"Failed to check {url}: {str(e)}")
            
            time.sleep(self.check_interval)

if __name__ == "__main__":
    db_config = {
        'dbname': 'projectrecon',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost'
    }
    
    monitor = EndpointMonitor(
        db_config=db_config,
        urls_file='endpoints.txt',
        check_interval=20,  # 4 hours in seconds
        response_dir='responses'
    )
    
    monitor.run()