from db_manager import DatabaseManager
from db_operations import DatabaseOperations

db_config = {
    'dbname': 'test_monitor',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost'
}

db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)



endpoint_data = {
    'url': 'https://google.com',
    'old_status_code': 111,
    'new_status_code': 1111,
    'old_size': '20KB',
    'new_size': '108KB',
    'old_body_hash': 'old_hash',
    'new_body_hash': 'new_hash',
    'old_body_path': '/home/user/data/js/old_response',
    'new_body_path': '/home/user/data/js/new_response',
    'change_detected_at': '12/1/2025',
    'last_check': '14/1/2025'

}


endpoint_data2 = {
    'url': 'https://google.com2',
    'old_status_code': 222,
    'new_status_code': 2222,
    'old_size': '20KB',
    'new_size': '108KB',
    'old_body_hash': 'old_hash',
    'new_body_hash': 'new_hash',
    'old_body_path': '/home/user/data/js/old_response',
    'new_body_path': '/home/user/data/js/new_response',
    'change_detected_at': '12/1/2025',
    'last_check': '14/1/2025'

}


endpoint_data3 = {
    'url': 'https://google.com3',
    'old_status_code': 333,
    'new_status_code': 3333,
    'old_size': '20KB',
    'new_size': '108KB',
    'old_body_hash': 'old_hash',
    'new_body_hash': 'new_hash',
    'old_body_path': '/home/user/data/js/old_response',
    'new_body_path': '/home/user/data/js/new_response',
    'change_detected_at': '12/1/2025',
    'last_check': '14/1/2025'

}



# endpoint_id = db_ops.insert_operations().insert_endpoint(endpoint_data)
# endpoint_id = db_ops.insert_operations().insert_endpoint(endpoint_data2)
# endpoint_id = db_ops.insert_operations().insert_endpoint(endpoint_data3)



endpoint_data = {
    'old_status_code': '200',
    'new_status_code': '404',
    'old_size': '108KB',
    'new_size': '10KB',
    'old_body_hash': 'old_hash',
    'new_body_hash': 'new_hash',
    'old_body_path': '/home/user/data/js/old_response',
    'new_body_path': '/home/user/data/js/new_response',
    'change_detected_at': '15/1/2025',
    'last_check': '15/1/2025'

}# db_ops.insert_operations().insert_change(change_data)
# db_ops.update_operations().update_endpoint_data("d3f4bf4b-764c-4301-9d55-c9c7d064e7ef", endpoint_data)


# ------------------------- Program -----------------------

program_data = {
    'program_name': 'No-Google',
    'program_url': 'https://no.google.com/no-bounty',
    'acquisitions': [''],
    'email': 'no-bounty@google.com',
    'report_form': None
}

# db_ops.insert_operations().insert_program(program_data)
# result  = db_ops.query_operations().check_program_exists("Google")
# print(result)

# -------------------- Mobile Target ----------------------

mobile_target_data = {
    'program_id': '717c571a-90ab-418c-9951-002547519431',
    'target_package': 'spkg_123s4',
    'target_apk': 'absacde',
    'technology': [''],
    'download_url': None,
    'vulnerability_reported': [{'Strandhog'}]
}

mobile_target_data = {
    'program_id': '35e0554a-a8ba-4785-94c4-5b596093394f',
    'target_package': 'dddddddddddddddddd',
    'target_apk': 'ddddddddddddddd',
    'technology': [],
    'download_url': None,
    'vulnerability_reported': []
}

# id = db_ops.insert_operations().insert_mobile_target(mobile_target_data)
# print(id)

web_target_data = {
    'program_id': '717c571a-90ab-418c-9951-002547519431',
    'target_domain': 'sub.google.com',
    'technology': [''],
    'status_code': 200,
    'port': 443,
    'host': None,
    'ipv4': [''],
    'ipv6': [''],
    'response_time': '20ms',
    'webserver': 'AWS',
    'vulnerability_reported': ['RCE', 'OAuth']
}

# id = db_ops.insert_operations().insert_web_target(web_target_data)
# print("Web target id: ", id)
# print("Mobile Exists: ", db_ops.query_operations().check_mobile_target_exists('pkg_123'))
# print("Web Exists: ", db_ops.query_operations().check_web_target_exists('sub.google.com'))
# 
# mobile_target_vuln_data = {'vulnerability_reported': 'bbbb'}
# print(db_ops.update_operations().update_mobile_target_vuln('99ce9e2c-b8ce-41a6-9ccf-f41b9e0c2d81', mobile_target_vuln_data))
# 
# target_data =db_ops.query_operations().get_mobile_target_data(target_id='701a0ab9-03b9-433e-b56b-a4388b30b82c')
# 
# (target_id, program_id, target_package, target_apk, technology, download_url, vulnerability_reported, created_at) = target_data[0]
# 
# print(vulnerability_reported)

print(db_ops.query_operations().check_mobile_target_vuln_exists(vulnerability_reported="Strandhog",target_package='dddddddddddddddddd'))

# print(db_ops.query_operations().get_mobile_target_data(target_id='99ce9e2c-b8ce-41a6-9ccf-f41b9e0c2d81'))