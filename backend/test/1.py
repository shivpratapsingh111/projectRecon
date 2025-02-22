from app.config.db_config  import db_config
from app.db.db_operations import DatabaseOperations
from app.db.db_manager import DatabaseManager
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)


print(db_ops.insert_operations().insert_web_target_new("2d1452ea-3cbd-47dc-8c9d-520cd0618e30", "asddrtsssas.com"))