# main.py
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



    def run(self, url):
        res = self.db_ops.query_operations().get_endpoint_data(url)
        print(res)



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
    
    monitor.run(url="https://0.0.0.0:8080")