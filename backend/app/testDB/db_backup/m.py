# main.py
import argparse
import sys
from pathlib import Path
from url_monitor.monitor import URLMonitor
from url_monitor.config import load_config
from url_monitor.logger import setup_logger

def parse_arguments():
    parser = argparse.ArgumentParser(description='URL Monitoring System')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--url', help='Single URL to monitor')
    group.add_argument('-f', '--file', help='File containing URLs (one per line)')
    parser.add_argument('-i', '--interval', type=int, default=10,
                       help='Monitoring interval in seconds (default: 300)')
    return parser.parse_args()

def load_urls_from_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        sys.exit(1)

def main():
    args = parse_arguments()
    logger = setup_logger()
    config = load_config()
    
    urls = [args.url] if args.url else load_urls_from_file(args.file)
    
    monitor = URLMonitor(urls, config, logger)
    monitor.start_monitoring(args.interval)

if __name__ == "__main__":
    main()