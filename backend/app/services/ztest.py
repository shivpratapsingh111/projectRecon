import subprocess

def check_tools():
    command = ["bash", "scripts/checkTools.sh"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.stdout.strip() == '0':
        print('Not Present')
    elif result.stdout.strip() == '1':
        print('Present')

check_tools()
