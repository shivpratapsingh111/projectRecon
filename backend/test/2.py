def are_all_commands_completed(data):
    """
    Check if all commands in the data have status 'completed'.

    :param data: Dictionary containing group_name, domains, and commands
    :return: True if all commands have 'completed' status, False otherwise
    """
    # Loop through all domains
    for domain_id, domain_data in data.get('domains', {}).items():
        commands = domain_data.get('commands', {})
        # Loop through all commands
        for command_name, command_data in commands.items():
            if command_data.get('status') != 'completed':
                return False  # Return False immediately if any status is not 'completed'
    return True  # Return True if all commands are 'completed'

# Example Usage
data = {
    'group_name': 'nt',
    'domains': {
        '99648e46-2225-41eb-b72d-2e9f6a55bcd3': {
            'domain_name': 'thecyberboy.com',
            'commands': {
                'assetfinder': {
                    'command_name': 'assetfinder',
                    'pid': 169839,
                    'command': 'echo thecyberboy.com | assetfinder',
                    'status': 'completed',
                    'start_time': '18:39:52, Wednesday, 18-12-2024',
                    'return_code': 0
                },
                'subfinder': {
                    'command_name': 'subfinder',
                    'pid': 169836,
                    'command': 'echo thecyberboy.com | subfinder',
                    'status': 'completed',
                    'start_time': '18:39:52, Wednesday, 18-12-2024',
                    'return_code': 0
                },
                'subdominator': {
                    'command_name': 'subdominator',
                    'pid': 169859,
                    'command': 'subdominator -d thecyberboy.com',
                    'status': 'completed',
                    'start_time': '18:39:52, Wednesday, 18-12-2024',
                    'return_code': 0
                }
            }
        }
    }
}

# Test the function
result = are_all_commands_completed(data)
print("All commands completed:", result)  # Output: True
