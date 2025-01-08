# url_monitor/monitor.py
import requests
import time
from datetime import datetime
from typing import List
from .db import Database, URLCheck

class URLMonitor:
    def __init__(self, urls: List[str], config: dict, logger):
        self.urls = urls
        self.db = Database(config['database'])
        self.logger = logger
        self.session = requests.Session()
    
    def check_url(self, url: str) -> URLCheck:
        """Perform a single URL check"""
        try:
            response = self.session.get(url, timeout=30)
            return URLCheck(
                url=url,
                status_code=response.status_code,
                response_body=response.text,
                timestamp=datetime.now()
            )
        except requests.RequestException as e:
            self.logger.error(f"Error checking {url}: {str(e)}")
            return URLCheck(
                url=url,
                status_code=-1,
                response_body=str(e),
                timestamp=datetime.now()
            )
    
    def compare_checks(self, current: URLCheck, previous: List[URLCheck]):
        """Compare current check with previous checks and log changes"""
        if not previous:
            self.logger.info(f"First check for {current.url}: Status {current.status_code}")
            return
        
        last_check = previous[0]
        if current.status_code != last_check.status_code:
            self.logger.warning(
                f"Status code changed for {current.url}: "
                f"{last_check.status_code} -> {current.status_code}"
            )
        
        if current.response_body != last_check.response_body:
            self.logger.warning(f"Response body changed for {current.url}")
    
    def monitor_url(self, url: str):
        """Monitor a single URL and process results"""
        current_check = self.check_url(url)
        previous_checks = self.db.get_last_checks(url)
        
        self.compare_checks(current_check, previous_checks)
        self.db.save_check(current_check)
    
    def start_monitoring(self, interval: int):
        """Start the monitoring loop"""
        self.logger.info(f"Starting monitoring of {len(self.urls)} URLs")
        
        try:
            while True:
                for url in self.urls:
                    self.monitor_url(url)
                self.logger.info(f"Sleeping for {interval} seconds")
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        finally:
            self.db.close()