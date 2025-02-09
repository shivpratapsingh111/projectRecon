from app.testDB.not_needed.db_manager import DatabaseManager
from app.testDB.not_needed.db_operations import DatabaseOperations

db_config = {
    'dbname': 'test_monitor',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost'
}

db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)



# endpoint_data = {
#     'url': 'https://google.com',
#     'old_status_code': 111,
#     'new_status_code': 1111,
#     'old_response_size': '20KB',
#     'new_response_size': '108KB',
#     'old_body_hash': 'old_hash',
#     'new_body_hash': 'new_hash',
#     'old_body_file_path': '/home/user/data/js/old_response',
#     'new_body_file_path': '/home/user/data/js/new_response',
#     'change_detected_at': '12/1/2025',
#     'last_check': '14/1/2025'

# }


# endpoint_data2 = {
#     'url': 'https://google.com2',
#     'old_status_code': 222,
#     'new_status_code': 2222,
#     'old_response_size': '20KB',
#     'new_response_size': '108KB',
#     'old_body_hash': 'old_hash',
#     'new_body_hash': 'new_hash',
#     'old_body_file_path': '/home/user/data/js/old_response',
#     'new_body_file_path': '/home/user/data/js/new_response',
#     'change_detected_at': '12/1/2025',
#     'last_check': '14/1/2025'

# }




# endpoint_id = db_ops.insert_operations().insert_endpoint(endpoint_data)
# endpoint_id = db_ops.insert_operations().insert_endpoint(endpoint_data2)
# endpoint_id = db_ops.insert_operations().insert_endpoint(endpoint_data3)



# db_ops.insert_operations().insert_change(change_data)
# db_ops.update_operations().update_endpoint_data("d3f4bf4b-764c-4301-9d55-c9c7d064e7ef", endpoint_data)
# print("Mobile Exists: ", db_ops.query_operations().check_mobile_target_exists('pkg_123'))
# print("Web Exists: ", db_ops.query_operations().check_web_target_exists('sub.google.com'))


# ------------------------- Program -----------------------


program_data = {
    'program_name': 'Bolt',
    'program_url': 'https://bolt.eu/no-bounty',
    'acquisitions': [''],
    'email': 'no-bounty@bolt.com',
    'report_form': None
}
program_data1 = {
    'program_name': 'Carry1st',
    'program_url': 'https://carry1st.com/no-bounty',
    'acquisitions': [''],
    'email': 'no-bounty@carry1st.com',
    'report_form': None
}

program_id = db_ops.insert_operations().insert_program(program_data)
program_id1 = db_ops.insert_operations().insert_program(program_data1)
# result  = db_ops.query_operations().check_program_exists("Google")
# print(result)


web_target_data = {
    'program_id': program_id,
    'target_domain': 'assets.ab-destinations.bolt.eu',
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
web_target_data1 = {
    'program_id': program_id1,
    'target_domain': 'cup.carry1st.com',
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

target_id = db_ops.insert_operations().insert_web_target(web_target_data)
target_id1 = db_ops.insert_operations().insert_web_target(web_target_data1)





endpoint_data_g1 = {
    'program_id': program_id,
    'target_id': target_id,
    'scan_name': 'Test-Scan',
    'scan_interval': 60,
    'status': 'active',
    'url': 'https://assets.ab-destinations.bolt.eu/72807e1b-46be15b9884d53a547a2.js',
    'old_status_code': 404,
    'new_status_code': 200,
    'old_response_size': '20KB',
    'new_response_size': '108KB',
    'old_body_hash': 'b8c9d9037af6724a49241b8b9a5a9dd1d3cc1c5e1a0aa31c8d06168af8ab07eb',
    'new_body_hash': '3ddf3b7e0bd4dc97972fd9f00e52b163b6b798b149ee5b2af15b9477334b349f',
    'old_body_file_path': '/home/retro/projectRecon-Data/monitoring/Test_Scan_APi/responses/accounts.google.com_.html',
    'new_body_file_path': '/home/retro/projectRecon-Data/monitoring/Test_Scan_APi/responses/accounts.google.com_.html_new',
    'change_detected_at': '2025-01-15 19:34:08.789826+05:30',
    'need_review': True,
    'last_check': '2025-01-15 19:34:08.795469'

}

endpoint_data_g2 = {
    'program_id': program_id,
    'target_id': target_id,
    'scan_name': 'Test-Scan',
    'scan_interval': 60,
    'status': 'active',
    'url': 'https://assets.ab-destinations.bolt.eu/appsflyer.min.js',
    'old_status_code': 404,
    'new_status_code': 200,
    'old_response_size': '20KB',
    'new_response_size': '108KB',
    'old_body_hash': 'b8c9d9037af6724a49241b8b9a5a9dd1d3cc1c5e1a0aa31c8d06168af8ab07eb',
    'new_body_hash': '3ddf3b7e0bd4dc97972fd9f00e52b163b6b798b149ee5b2af15b9477334b349f',
    'old_body_file_path': None,
    'new_body_file_path': None,
    'change_detected_at': '2025-01-15 19:34:08.789826+05:30',
    'need_review': True,
    'last_check': '2025-01-15 19:34:08.795469'

}

endpoint_data_g3 = {
    'program_id': program_id,
    'target_id': target_id,
    'scan_name': 'Test-Scan',
    'scan_interval': 60,
    'status': 'active',
    'url': 'https://assets.ab-destinations.bolt.eu/731-d0f1afd3d98182ff7489.js',
    'old_status_code': 404,
    'new_status_code': 200,
    'old_response_size': '20KB',
    'new_response_size': '108KB',
    'old_body_hash': 'b8c9d9037af6724a49241b8b9a5a9dd1d3cc1c5e1a0aa31c8d06168af8ab07eb',
    'new_body_hash': '3ddf3b7e0bd4dc97972fd9f00e52b163b6b798b149ee5b2af15b9477334b349f',
    'old_body_file_path': None,
    'new_body_file_path': None,
    'change_detected_at': '2025-01-15 19:34:08.789826+05:30',
    'need_review': True,
    'last_check': '2025-01-15 19:34:08.795469'

}


endpoint_data_y1 = {
    'program_id': program_id1,
    'target_id': target_id1,
    'scan_name': 'Test-Scan',
    'scan_interval': 60,
    'status': 'active',
    'url': 'https://cup.carry1st.com/misc/form-single-submit.js',
    'old_status_code': 404,
    'new_status_code': 200,
    'old_response_size': '108KB',
    'new_response_size': '10KB',
    'old_body_hash': '0e75f62e9e1e3876931dd0de6fe3a7a1b9eea6e2378f34e746a862ab552c588f',
    'new_body_hash': '2f3dd6b46b051ca9c94c4fd577cb7f8c7e3318cd2afe3316fff9ec7422300cd3',
    'old_body_file_path': None,
    'new_body_file_path': None,
    'change_detected_at': '2025-01-15 19:23:00.755402+05:30',
    'need_review': True,
    'last_check': '2025-01-15 19:34:08.795469'

}
endpoint_data_y2 = {
    'program_id': program_id1,
    'target_id': target_id1,
    'scan_name': 'Test-Scan',
    'scan_interval': 60,
    'status': 'active',
    'url': 'https://cup.carry1st.com/misc/drupal.js',
    'old_status_code': 404,
    'new_status_code': 200,
    'old_response_size': '108KB',
    'new_response_size': '10KB',
    'old_body_hash': '0e75f62e9e1e3876931dd0de6fe3a7a1b9eea6e2378f34e746a862ab552c588f',
    'new_body_hash': '2f3dd6b46b051ca9c94c4fd577cb7f8c7e3318cd2afe3316fff9ec7422300cd3',
    'old_body_file_path': None,
    'new_body_file_path': None,
    'change_detected_at': '2025-01-15 19:23:00.755402+05:30',
    'need_review': True,
    'last_check': '2025-01-15 19:34:08.795469'

}
endpoint_data_y3 = {
    'program_id': program_id1,
    'target_id': target_id1,
    'scan_name': 'Test-Scan',
    'scan_interval': 60,
    'status': 'active',
    'url': 'https://cup.carry1st.com/sites/all/modules/esports/tournament/js/password_toggle.js',
    'old_status_code': 404,
    'new_status_code': 200,
    'old_response_size': '108KB',
    'new_response_size': '10KB',
    'old_body_hash': '0e75f62e9e1e3876931dd0de6fe3a7a1b9eea6e2378f34e746a862ab552c588f',
    'new_body_hash': '2f3dd6b46b051ca9c94c4fd577cb7f8c7e3318cd2afe3316fff9ec7422300cd3',
    'old_body_file_path': None,
    'new_body_file_path': None,
    'change_detected_at': '2025-01-15 19:23:00.755402+05:30',
    'need_review': True,
    'last_check': '2025-01-15 19:34:08.795469'

}

# endpoint_id = db_ops.insert_operations().insert_endpoint(endpoint_data_g1)
endpoint_id = db_ops.insert_operations().insert_endpoint(endpoint_data_g2)
endpoint_id = db_ops.insert_operations().insert_endpoint(endpoint_data_g3)
# endpoint_id1 = db_ops.insert_operations().insert_endpoint(endpoint_data_y1)
endpoint_id1 = db_ops.insert_operations().insert_endpoint(endpoint_data_y2)
endpoint_id1 = db_ops.insert_operations().insert_endpoint(endpoint_data_y3)


# -------------------- Mobile Target ----------------------

mobile_target_data = {
    'program_id': program_id,
    'target_package': 'com.bolt.android',
    'target_apk': 'Bolt APK',
    'technology': [''],
    'download_url': None,
    'vulnerability_reported': ['Strandhog']
}

mobile_target_data1 = {
    'program_id': program_id1,
    'target_package': 'com.carry1st.android',
    'target_apk': 'Carry1st APK',
    'technology': [],
    'download_url': None,
    'vulnerability_reported': [],
}

mobile_target_id = db_ops.insert_operations().insert_mobile_target(mobile_target_data)
mobile_target_id1 = db_ops.insert_operations().insert_mobile_target(mobile_target_data1)



# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# mobile_target_vuln_data = {'vulnerability_reported': 'bbbb'}
# print(db_ops.update_operations().update_mobile_target_vuln('99ce9e2c-b8ce-41a6-9ccf-f41b9e0c2d81', mobile_target_vuln_data))
# 
# target_data =db_ops.query_operations().get_mobile_target_data(target_id='701a0ab9-03b9-433e-b56b-a4388b30b82c')
# 
# (target_id, program_id, target_package, target_apk, technology, download_url, vulnerability_reported, created_at) = target_data[0]
# 
# print(vulnerability_reported)

# print(db_ops.query_operations().check_mobile_target_vuln_exists(vulnerability_reported="Strandhog",target_package='dddddddddddddddddd'))

# print(db_ops.query_operations().get_mobile_target_data(target_id='99ce9e2c-b8ce-41a6-9ccf-f41b9e0c2d81'))
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------