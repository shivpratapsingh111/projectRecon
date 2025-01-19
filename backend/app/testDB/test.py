from app.services.monitor_endpoints.db.db_manager import DatabaseManager
from app.services.monitor_endpoints.db.db_operations import DatabaseOperations

db_config = {
    'dbname': 'test_monitor',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost'
}

db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

# db_ops.update_operations().update_need_review_endpoint('c10ddb8f-33f3-44a3-9aa3-762f9f32a485')

# result = db_ops.query_operations().get_endpoints_data_by_status('active')
# print(result[0])
# print(result[1])
# program_id = '509a2075-9a65-468e-b14f-e1899827c537'
# result = db_ops.query_operations().get_program_name(program_id)
# 
# print(result[0][0])

target_id, program_id = db_ops.query_operations().get_target_and_program_id('cup.carry1st.com')
print(f"Target Id {target_id}")
print(f"Program Id {program_id}")
