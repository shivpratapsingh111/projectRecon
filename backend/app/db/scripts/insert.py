import os
import json
import uuid
import argparse
import psycopg2
from psycopg2 import sql
from typing import List, Dict, Optional

class DatabaseImporter:
    def __init__(self, db_name: str, host: str = 'localhost', port: int = 5432, 
                 user: str = 'postgres', password: str = ''):
        """
        Initialize database connection parameters
        
        :param db_name: Name of the database to create/connect
        :param host: Database host (default: localhost)
        :param port: Database port (default: 5432)
        :param user: PostgreSQL admin username
        :param password: PostgreSQL admin password
        """
        self.db_name = db_name
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        
        # Database creation and table creation SQL statements
        self.CREATE_EXTENSIONS = "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""
        
        self.CREATE_PROGRAMS_TABLE = """
        CREATE TABLE IF NOT EXISTS programs (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            program_name TEXT NOT NULL,
            program_url TEXT,
            acquisitions TEXT[],
            email TEXT,
            report_form TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        self.CREATE_WEB_TARGETS_TABLE = """
        CREATE TABLE IF NOT EXISTS web_targets (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
            target_domain TEXT NOT NULL,
            technology TEXT[],
            status_code INTEGER,
            port INTEGER,
            host INET,
            ipv4 TEXT[],
            ipv6 TEXT[],
            response_time TEXT,
            webserver TEXT,
            vulnerability_reported TEXT[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        self.CREATE_MOBILE_TARGETS_TABLE = """
        CREATE TABLE IF NOT EXISTS mobile_targets (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
            target_package TEXT UNIQUE NOT NULL,
            target_apk TEXT NOT NULL,
            technology TEXT[],
            download_url TEXT,
            vulnerability_reported TEXT[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        self.CREATE_ENDPOINTS_TABLE = """
        CREATE TABLE IF NOT EXISTS monitor_endpoints (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
            target_id UUID REFERENCES web_targets(id) ON DELETE CASCADE,
            scan_name TEXT,
            scan_interval INTEGER DEFAULT 4,
            status TEXT DEFAULT 'active',
            url TEXT UNIQUE NOT NULL,
            old_status_code INTEGER,
            new_status_code INTEGER,
            old_response_size TEXT,
            new_response_size TEXT,
            old_body_hash TEXT,
            new_body_hash TEXT,
            old_body_file_path TEXT,
            new_body_file_path TEXT,
            change_detected_at TEXT,
            need_review BOOLEAN DEFAULT FALSE,
            last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    def check_db_exists(self) -> bool:
        """
        Check if the database already exists
        
        :return: Boolean indicating database existence
        """
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            conn.autocommit = True
            cur = conn.cursor()
            
            cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (self.db_name,))
            exists = cur.fetchone() is not None
            
            cur.close()
            conn.close()
            
            return exists
        except Exception as e:
            print(f"Error checking database existence: {e}")
            return False
    
    def create_database_and_tables(self, db_exits):
        """
        Create database and initialize tables
        """
        try:
            if not db_exits:
                # Connect to postgres database to create new database
                conn = psycopg2.connect(
                    dbname='postgres',
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port
                )
                conn.autocommit = True
                cur = conn.cursor()
                
                # Create database
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db_name)))
            
                # Close connection to postgres and connect to new database
                cur.close()
                conn.close()
            
            # Connect to new database
            conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            conn.autocommit = True
            cur = conn.cursor()
            
            # Create UUID extension
            cur.execute(self.CREATE_EXTENSIONS)
            
            # Create tables
            cur.execute(self.CREATE_PROGRAMS_TABLE)
            cur.execute(self.CREATE_WEB_TARGETS_TABLE)
            # Leaving mobile_targets and monitor_endpoints tables empty as requested
            
            cur.close()
            conn.close()
            
            print(f"Database {self.db_name} created successfully with tables.")
        except Exception as e:
            print(f"Error creating database and tables: {e}")
    
    def parse_httpx_subdomains(self, httpx_file: str) -> Dict[str, Dict]:
        """
        Parse JSONL file with subdomain information
        
        :param httpx_file: Path to httpx_subdomains.json file
        :return: Dictionary mapping subdomains to their details
        """
        subdomain_details = {}
        
        if not os.path.exists(httpx_file):
            print(f"Httpx subdomains file not found: {httpx_file}")
            return subdomain_details
        
        with open(httpx_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    subdomain = data.get('input', '')
                    
                    if subdomain:
                        subdomain_details[subdomain] = {
                            'technology': data.get('tech', []),
                            'status_code': data.get('status_code'),
                            'port': data.get('port'),
                            'host': data.get('host'),
                            'ipv4': data.get('a', []),
                            'ipv6': data.get('aaaa', []) if 'aaaa' in data else [],
                            'response_time': data.get('time'),
                            'webserver': data.get('webserver')
                        }
                except json.JSONDecodeError:
                    print(f"Error decoding JSON line: {line}")
        
        return subdomain_details
    

    def get_program_id(self, json_file_name, group_name):
        """
        Takes a JSON file name and group name, and returns the program ID of the group.
        """
        with open(json_file_name, 'r') as file:
            data = json.load(file)
            groups = data.get("groups", {})

            for program_id, group_details in groups.items():
                if group_details.get("group_name") == group_name:
                    return program_id
        return None 

    def get_domain_id(self, json_file_name, program_id, domain_name):
        """
        Takes a JSON file name, program ID, and domain name, and returns the UUID of the specified domain.
        """
        with open(json_file_name, 'r') as file:
            data = json.load(file)
            groups = data.get("groups", {})

            group_details = groups.get(program_id)
            if group_details:
                domains = group_details.get("domains", {})
                for domain_id, domain_details in domains.items():
                    if domain_details.get("domain_name") == domain_name:
                        return domain_id

        return None 


    def import_directory_data(self, directory_path: str, json_file_name: str):
        """
        Import data from directory into database
        
        :param directory_path: Root directory containing program data
        """
        try:
            # Connect to database
            conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            conn.autocommit = True
            cur = conn.cursor()
            
            # Get program name from directory name
            program_name = os.path.basename(directory_path)
            program_id = self.get_program_id(json_file_name, program_name)
            if program_id is None:
                print(f"Error: program_id is not found in json data file provided for {program_name}")
                exit()

            cur.execute("""
                INSERT INTO programs (id, program_name) 
                VALUES (%s, %s) 
            """, (program_id, program_name,))
            
            targets_file = os.path.join(directory_path, 'targets.txt')
            inserted_domains = set()
            
            if os.path.exists(targets_file):
                with open(targets_file, 'r') as f:
                    targets = [line.strip() for line in f if line.strip()]
                
                for target in targets:
                    if target not in inserted_domains:
                        target_id = self.get_domain_id(json_file_name, program_id, target)
                        if target_id is None:
                            print(f"Error: ID not found for domain [{target}] in json data file.")
                            exit()
                        cur.execute("""
                            INSERT INTO web_targets (id, program_id, target_domain) 
                            VALUES (%s, %s, %s)
                        """, (target_id, program_id, target))
                        inserted_domains.add(target)
                    
                    # Parse subdomain details for this specific target
                    httpx_file = os.path.join(directory_path, target, 'subdomains', 'httpx_subdomains.json')
                    subdomain_details = self.parse_httpx_subdomains(httpx_file)
                    
                    # Find and insert subdomains for this target
                    subdomains_file = os.path.join(directory_path, target, 'subdomains', 'subdomains.txt')
                    if os.path.exists(subdomains_file):
                        with open(subdomains_file, 'r') as f:
                            subdomains = [line.strip() for line in f if line.strip()]
                        
                        # Insert subdomains into web_targets
                        for subdomain in subdomains:
                            # Get details for this specific subdomain
                            details = subdomain_details.get(subdomain, {})
                            
                            cur.execute("""
                                INSERT INTO web_targets (
                                    program_id, 
                                    target_domain, 
                                    technology, 
                                    status_code, 
                                    port, 
                                    host, 
                                    ipv4, 
                                    ipv6, 
                                    response_time, 
                                    webserver
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                program_id, 
                                subdomain, 
                                details.get('technology'), 
                                details.get('status_code'), 
                                details.get('port'), 
                                details.get('host'), 
                                details.get('ipv4'), 
                                details.get('ipv6'), 
                                details.get('response_time'), 
                                details.get('webserver')
                            ))
                            inserted_domains.add(subdomain)
            
            cur.close()
            conn.close()
            
            print(f"Data imported successfully for program: {program_name}")
        
        except Exception as e:
            print(f"Error importing directory data: {e}")
    
    def run_import(self, directory_path: str, json_file_name: str):
        """
        Main method to run database import process
        
        :param directory_path: Root directory containing program data
        """
        # Check if database exists
        db_exits = self.check_db_exists()
        if db_exits:
            print(f"Database {self.db_name} already exists.")
        
        # Create database and tables
        self.create_database_and_tables(db_exits)
        
        # Import data
        self.import_directory_data(directory_path, json_file_name)

def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Import program and data files into the database.")
    parser.add_argument("-dir", "--directory", required=True, help="Path to the directory containing program data.")
    parser.add_argument("-config", "--config", required=True, help="Path to the JSON data file.")
    
    # Parse the command-line arguments
    args = parser.parse_args()
    directory_path = args.directory.strip('/')
    json_file_name = args.config

    # Initialize the DatabaseImporter
    importer = DatabaseImporter(
        db_name='ttttttttttt',
        user='postgres',
        password='postgres'
    )
    
    # Run the import process with the provided arguments
    importer.run_import(directory_path, json_file_name)

# Entry point for the script
if __name__ == "__main__":
    main()
