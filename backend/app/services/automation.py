def are_all_commands_completed(group_name):
    """
    Check if all commands in the data have status 'completed'.
    :param data: Dictionary containing group_name, domains, and commands
    :return: True if all commands have 'completed' status, False otherwise
    """
    while True:
        data = manager.command_monitor(group_name)
        # Loop through all domains
        for domain_id, domain_data in data.get('domains', {}).items():
            commands = domain_data.get('commands', {})
            # Loop through all commands
            for command_name, command_data in commands.items():
                if command_data.get('status') != 'completed':
                    break  # Return False immediately if any status is not 'completed'
        return data  # Return True if all commands are 'completed'
        time.sleep(5)

def func_nuclei(group_name, domain_list):

    # Store results for each domain
    group_results = {}
    
    # Execute commands for a group of domains
    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/nuclei"
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(f"{result_dir}/logs", exist_ok=True)
        commands = [
            ("nuclei", f"nuclei -l {root_Data_Dir}/{group_name}/{domain}/subdomains/{subdomainResults} -t ~/nuclei-templates/ -c 50 -fr -rl 20 -timeout 20 -o {result_dir}/{nucleiResults}", f"{result_dir}/{nucleiResults}_stdout", f"{result_dir}/logs/{nucleiResults}")
        ]
        
        # Execute commands and store the result
        group_results[domain] = manager.command_executor(group_name, domain_list, domain, commands, scan_dir="subdomains")
 
    final_monitoring_result = are_all_commands_completed(group_name)
    print(f"nuclei Completed")#!/usr/bin/python3
import sys
import os
import shutil
import subprocess
import threading
import requests
from colorama import Fore, Back, Style
import argparse

parser = argparse.ArgumentParser()

# Test
parser.add_argument("-test", action='store_true', help="It will call test.sh in scripts directory")

# Config
parser.add_argument("-update", action='store_true', help="Update to latest version")
parser.add_argument("-example", action='store_true', help="Example: python3 main.py -f domains.txt -all https://burpcollaborator.link")
parser.add_argument("-org", action='store_true', help="Organise the results, by combining results of all provided domains into a centralised folder")
parser.add_argument("-dir", help="provide directory name")

# Flags
parser.add_argument("-all", help="[Subdomain & URL Enum, Subdomain Takeover, SSRF, XSS, Nuclei]: Provide Link for SSRF Testing")
parser.add_argument("-f", help="Give file name consisting of target domains")
parser.add_argument("-ssrf", help="SSRF Testing: Provide Burp Collaborator/Server link")
parser.add_argument("-nmap", action='store_true', help="Nmap Scan")
parser.add_argument("-xss", action='store_true', help="XSS testing")
parser.add_argument("-tkovr", action='store_true', help="Subdomain Takeover check")
parser.add_argument("-nuclei", action='store_true', help="Use Nuclei")
parser.add_argument("-fuzz", action='store_true', help="Fuzz for endpoints")
parser.add_argument("-js", action='store_true', help="Analyse JS files for juicy stuff")
parser.add_argument("-urls", nargs='?', const='ps', help="URL Enumeration, ac: for crawling, ps: for passive gathering, provide no value for both")
parser.add_argument("-sub", nargs='?', const='ps', help="Enumerating Subdomains, ac: for active, ps: for passive, provide no value for both")
parser.add_argument("-amass_t", help="Amass timeout [Default 30 mins] [Use 0 for no timeout] [-amass_t 30 for 30 min timeout ]")


args = parser.parse_args()


# github repo to update
REPO_URL = 'https://github.com/Kirosci/Project-Recon.git'


def messageBefore(task):
    print(Fore.BLUE + f"[+] [Task: {task}]", end=' ') 
    print(Fore.YELLOW + "[Status: In progress]", end=' ')
    print(Style.RESET_ALL)

def messageAfter(task, info):
    print(Fore.BLUE + f"[+] [Task: {task}]", end=' ') 
    print(Fore.GREEN + "[Status: Completed]", end=' ')
    print(Fore.CYAN + f"[Info: {info}]", end=' ')
    print(Style.RESET_ALL)

def notProvided(task):
    print(Fore.RED + f"[+] [Task: {task}]", end=' ') 
    print(Fore.BLUE + "[Status: Argument Not Provided]")
    print(Style.RESET_ALL)

def errorMessage(msg):
    print(Fore.RED + f"[+] [Error]", end=' ') 
    print(Fore.BLUE + f"[+] [Info: {msg}]")
    print(Style.RESET_ALL)




# ---

# Template for new flag's function

# # For $YOUR TASK 
# def $FUNCTION_NAME(cmd):
#     messageBefore("$YOUR_MESSAGE")
#     p_$FUNCTION_NAME = subprocess.Popen(cmd, shell=True).wait()
#     messageAfter("YOUR_MESSAGE", "YOUR_INFO")

# ---

# Calling test.sh file in scripts directory
def callTest(cmd):
    messageBefore("Test")
    p_callTest = subprocess.Popen(cmd, shell=True).wait()
    messageAfter("Test", "Calling test.sh file")

# For updating the tool 
def update(cmd):
    messageBefore("Update")
    p_update = subprocess.Popen(cmd, shell=True).wait()
    messageAfter("Update", "Updated Project-Recon")

# For organising results 
def organise(cmd):
    messageBefore("Organise")
    p_organise = subprocess.Popen(cmd, shell=True).wait()
    messageAfter("Organise", "Organising Done")

# For gathering subdomains
def subdomains(cmd):
    messageBefore("Subdomain Enumeration")
    p_subdomain = subprocess.Popen(cmd,shell=True).wait()
    messageAfter("Subdomain Enumeration", "Results saved in subdomains.txt & liveSubdomains.txt")


# For checking subdomain takeover 
def subTakeover(cmd):
    messageBefore("Subdomain Takeover")
    p_urls= subprocess.Popen(cmd, shell=True).wait()
    messageAfter("Subdomain Takeover", "Results saved in subTakeovers.txt")

# For gathering urls 
def urls(cmd):
    messageBefore("URL Gathering")
    p_urls= subprocess.Popen(cmd,shell=True).wait()
    messageAfter("URL Gathering", "Results saved in urls.txt")

# Sanning SSRF
def ssrf(cmd): 
    messageBefore("SSRF")
    p_urls= subprocess.Popen(cmd,shell=True).wait()
    messageAfter("SSRF", "Results saved in ssrfUrls.txt | Check if you get any pingbacks")

# Scanning SSRF
def xss(cmd):
    messageBefore("XSS")
    p_urls= subprocess.Popen(cmd,shell=True).wait()
    messageAfter("XSS", "Results saved in xss.txt")

# Nuclei
def nuclei(cmd):
    messageBefore("Nuceli")
    p_urls= subprocess.Popen(cmd,shell=True).wait()
    messageAfter("Nuceli", "Results Saved in nuclei.txt")

# Fuzzing
def fuzz(cmd):
    messageBefore("Fuzzing")
    p_urls= subprocess.Popen(cmd,shell=True).wait()
    messageAfter("Fuzzing", "Results Saved in fuzz.txt and fuzz/")

# JS
def js(cmd):
    messageBefore("JS")
    p_urls= subprocess.Popen(cmd,shell=True).wait()
    messageAfter("JS", "Results Saved in js/")

# Nmap
def nmap(cmd):
    messageBefore("Nmap")
    p_urls= subprocess.Popen(cmd,shell=True).wait()
    messageAfter("Nmap", "Results Saved in nmap/ directory")

# Check internet connection 
def check_internet():
    try:
        response = requests.get("https://8.8.8.8", timeout=2)
        return True
    except requests.ConnectionError:
        return False
    
# Check tools
def check_tools():
    command = ["bash", "scripts/checkTools.sh"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.stdout.strip() == '0':
        return False
    elif result.stdout.strip() == '1':
        return True


def pseudoMain():
        # Handling sudden termination
    try:
        # Check Internet Connection
        if check_internet() and check_tools():
            # Get Target Domain name
            main_script_directory = os.path.dirname(os.path.abspath(__file__))
            target_directory = os.path.join(main_script_directory, 'Project-Recon')


            if args.update:
                cmdUpdate = "bash scripts/update.sh"
                thre_update = threading.Thread(target=update, args=(cmdUpdate,))
                thre_update.start()
                thre_update.join()
                sys.exit(1)
            elif args.test:
                cmdTest = "bash scripts/test.sh"
                thre_test = threading.Thread(target=callTest, args=(cmdTest,))
                thre_test.start()
                thre_test.join()                
                sys.exit(1)
            else:
                pass
                
# Check if file containing domains is provided
            if args.f:
                domain = args.f
                print(Back.WHITE, Fore.RED + '[Automating to hunt more and sleep less]', Style.RESET_ALL)

            else:
                if not args.update:
                    errorMessage("Provide a file containing domains")
                sys.exit(1) 

# Check if value for amass timeout is provided, else set  
            link = args.ssrf
            if args.amass_t:
                amassTimeout = args.amass_t
            else:
                amassTimeout = 1

# Check if -org flag is provided without -dir flag
            if args.org and args.dir:
                organiseDirectory = args.dir
            elif args.org:
                errorMessage("Provide directory name with -dir flag to save organised results in")
                sys.exit(1)
            elif args.dir:
                errorMessage("Why are you using -dir flag? Exiting...")
                sys.exit(1)



            if args.sub == 'ac':
                cmdSubdomains = f"bash scripts/subdomains.sh {domain} {amassTimeout} active"
            elif args.sub == 'ps': 
                cmdSubdomains = f"bash scripts/subdomains.sh {domain} {amassTimeout} passive"
            elif args.sub == 'both':
                cmdSubdomains = f"bash scripts/subdomains.sh {domain} {amassTimeout} both"
            elif args.sub == None:
                cmdSubdomains = f"bash scripts/subdomains.sh {domain} {amassTimeout} passive"
            else:
                errorMessage(f"`{args.sub}` is not supported by -sub flag")
                errorMessage("Pass`ac` for active | `ps` for passive | `both` for both active & passive with `-sub` flag")
                sys.exit(1)


            if args.urls == 'ac':
                cmdUrls = f"bash scripts/urls.sh {domain} active"
            elif args.urls == 'ps': 
                cmdUrls = f"bash scripts/urls.sh {domain} passive"
            elif args.urls == 'both':
                cmdUrls = f"bash scripts/urls.sh {domain} both"
            elif args.urls == None:
                cmdUrls = f"bash scripts/urls.sh {domain} passive"
            else:
                errorMessage(f"`{args.urls}` is not supported by -urls flag")
                errorMessage("Pass`ac` for active | `ps` for passive | `both` for both active & passive with `-urls` flag")
                sys.exit(1)

            if args.org:
                cmdOrganise = f"bash scripts/organise.sh {domain} {organiseDirectory}"


            cmdSubTakeover = f"bash scripts/subTakeover.sh {domain}"
            cmdSsrf = f"bash scripts/ssrf.sh {domain} {link}"
            cmdXss = f"bash scripts/xss.sh {domain}"
            cmdNuclei = f"bash scripts/nuclei.sh {domain}"
            cmdFuzz = f"bash scripts/fuzz.sh {domain}"
            cmdJs = f"bash scripts/js.sh {domain}"
            cmdNmap = f"bash scripts/nmap.sh {domain}"


            if args.all:
                
                # Enumerating Subdomains Start AND WAIT 
                thread_subdomains = threading.Thread(target=subdomains, args=(cmdSubdomains,))
                thread_subdomains.start()
                thread_subdomains.join()

                # URL Enumeration Start AND WAIT
                thread_urls = threading.Thread(target=urls, args=(cmdUrls,))
                thread_urls.start()
                thread_urls.join()

                #Analyzing JS files Start AND WAIT
                thread_js = threading.Thread(target=js, args=(cmdJs,))
                thread_js.start()
                thread_js.join()

                # Scanning for potential Subdomain Takeovers Start AND WAIT
                thread_subTakeover = threading.Thread(target=subTakeover, args=(cmdSubTakeover,))
                thread_subTakeover.start()
                thread_subTakeover.join()

                # Running Nuclei Start AND WAIT
                thread_nuclei = threading.Thread(target=nuclei, args=(cmdNuclei,))
                thread_nuclei.start()
                thread_nuclei.join()

                #Nmap Start AND WAIT
                thread_nmap = threading.Thread(target=nmap, args=(cmdNmap,))
                thread_nmap.start()
                thread_nmap.join()

                #Fuzzing subdomains Start AND WAIT
                thread_fuzz = threading.Thread(target=fuzz, args=(domain,))
                thread_fuzz.start()
                thread_fuzz.join()

                # Scanning for potential XSS Start AND WAIT
                thread_xss = threading.Thread(target=xss, args=(cmdXss,))
                thread_xss.start()
                thread_xss.join()

                # Scanning for potential SSRF Start AND WAIT
                link = args.all
                thread_ssrf = threading.Thread(target=ssrf, args=(cmdSsrf,))
                thread_ssrf.start()
                thread_ssrf.join()



            else:

        # Commented else for each argument, it was looking too chaotic and messy

                # Organising results thread start
                if args.org:
                    thread_organise = threading.Thread(target=organise, args=(cmdOrganise,))
                    thread_organise.start()
                # else:
                #     notProvided("Organise results")


                # Enumerating Subdomains thread Start AND WAIT
                if args.sub:
                    thread_subdomains = threading.Thread(target=subdomains, args=(cmdSubdomains,))
                    thread_subdomains.start()
                    thread_subdomains.join()
                # else:
                #     notProvided("Subdomains Enumeration")


                # Fuzzing subdomains Start AND WAIT
                if args.fuzz:
                    thread_fuzz = threading.Thread(target=fuzz, args=(cmdFuzz,))
                    thread_fuzz.start()
                    thread_fuzz.join()
                # else:
                #     notProvided("Fuzzing")

 
                # Subdomain Takeover thread Start AND WAIT
                if args.tkovr:
                    thread_subTakeover = threading.Thread(target=subTakeover, args=(cmdSubTakeover,))
                    thread_subTakeover.start()
                    thread_subTakeover.join()
                # else:
                #     notProvided("Subdomain Takeover")

 
                # URL Enumeration thread start AND WAIT
                if args.urls:
                    thread_urls = threading.Thread(target=urls, args=(cmdUrls,))
                    thread_urls.start()
                    thread_urls.join()
                # else:
                #     notProvided("URL Gathering")


                # SSRF testing thread Start AND WAIT
                if args.ssrf:
                    link = args.ssrf
                    thread_ssrf = threading.Thread(target=ssrf, args=(cmdSsrf,))
                    thread_ssrf.start()
                    thread_ssrf.join()
                # else:
                #     notProvided("SSRF")


                # Nuclei Scan thread Start AND WAIT
                if args.nuclei:
                    thread_nuclei = threading.Thread(target=nuclei, args=(cmdNuclei,))
                    thread_nuclei.start()
                    thread_nuclei.join()
                # else:
                #     notProvided("Nuclei")


                # XSS testing thread Start AND WAIT
                if args.xss:
                    thread_xss = threading.Thread(target=xss, args=(cmdXss,))
                    thread_xss.start()
                    thread_xss.join()
                # else:
                #     notProvided("XSS")


                # JS analyzing thread Start AND WAIT
                if args.js:
                    thread_js = threading.Thread(target=js, args=(cmdJs,))
                    thread_js.start()
                    thread_js.join()
                # else:
                #     notProvided("JS")

                
                #Nmap Start AND WAIT
                if args.nmap:
                    thread_nmap = threading.Thread(target=nmap, args=(cmdNmap,))
                    thread_nmap.start()
                    thread_nmap.join()
                # else:
                #     notProvided("JS")



        else:
            if not check_internet() and not check_tools():
                errorMessage("Internet is not working!")
                errorMessage("Required tools are not present!")
            elif not check_internet():
                errorMessage("Internet is not working!")
            elif not check_tools():
                errorMessage("Required tools are not present, Please run setup.sh")

    except KeyboardInterrupt:
        print("\n[Terminated: You pressed ctrl+c]")



def main():

    pseudoMain()

if __name__ == '__main__':
    main()