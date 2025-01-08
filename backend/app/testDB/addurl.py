import psycopg2
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="projectrecon",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()
query = "INSERT INTO endpoints (url) VALUES (%s) RETURNING id;"
value = "helllllllloooooooo"
cur.execute(query, (value,))
databases = cur.fetchall()
print("Content:", databases[0][0])
# for db in databases:
#     print(db[0])

# try:
#     conn = psycopg2.connect(**temp_config)
#     conn.autocommit = True  # Required for database creation
#     cur = conn.cursor()
# except Exception as e:
#     print("Error:", e)

# if __name__ == "__main__":
#     db_config = {
#         'dbname': 'projectrecon',
#         'user': 'postgres',
#         'password': 'postgres',
#         'host': 'localhost'
#     }
    
#     monitor = EndpointMonitor(
#         db_config=db_config,
#         urls_file='endpoints.txt',
#         check_interval=20,  # 4 hours in seconds
#         response_dir='responses'
#     )
    
#     monitor.run()