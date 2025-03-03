from app.config.db_config  import db_config
from app.db.db_operations import DatabaseOperations
from app.db.db_manager import DatabaseManager
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)


result = db_ops.query_operations().get_all_web_targets()
domain_list = [item[0] for item in result]
print(domain_list)