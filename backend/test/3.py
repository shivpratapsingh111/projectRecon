        
# List of selected tools to run
selected_tools = ["bbot", "subfinder", "cero"]  # Modify this array as needed
result_dir = "sss"
domain = "asdasd"


if not subdomain_enum.get("run", False):
    print("Subdomain enumeration is disabled.")
    return


include_api = subdomain_enum.get("includeApi", False)
tool_selection = subdomain_enum.get("toolSelection", False)
selected_tools = subdomain_enum.get("selectedTools", [])


cmd = {
    "bbot": f"bbot -t {domain} -f subdomain-enum -n bbot -o {result_dir} -y --modules asn azure_realm azure_tenant baddns_direct baddns_zone dnsbimi dnscaa dnscommonsrv github_codesearch github_org httpx hunterio internetdb ipneighbor oauth otx postman postman_download securitytxt shodan_dns sslcert subdomainradar --exclude-modules dnsbrute dnsbrute_mutations wayback",
    "subdominator": f"subdominator -d {domain} --no-color --disable-update-check -o {result_dir}/{subdominator}" + (" --config-path ~/.config/projectRecon/api-subdominator.txt" if include_api else ""),
    "subfinder": f"subfinder -d {domain} -sources chinaz,columbus,github,hunter,robtex,threatbook,whoisxmlapi,zoomeyeapi,virustotal,shodan,securitytrails,fofa,chaos,certspotter,censys,binaryedge,bevigil -no-color -disable-update-check -o {result_dir}/{subfinder}" + (" -provider-config ~/.config/projectRecon/api-subfinder.txt" if include_api else ""),
    
    "cero": f"cero {domain} | tee -a {result_dir}/{cero}",
    
    "sublist3r": f"cd ~/tools/Sublist3r && python3 sublist3r.py -d {domain} -o {result_dir}/{sublist3r}",
    
    "yass": f"yass {domain} -nc | tee -a {result_dir}/{yass}",
    
    "githubsubdomains": f"github-subdomains -d {domain} -raw -o {result_dir}/{githubsubdomains}",
    
    "gitlabsubdomains": f"github-subdomains -d {domain} | tee -a {result_dir}/{gitlabsubdomains}",
}
    

# Define all available commands
all_commands = [
    (
        "bbot",
        f"{cmd.get('bbot_cmd')}",
        f"{result_dir}/.logs/s_stdout",
        f"{result_dir}/.logs/sstderr"
    ),
    (
        "subdominator",
        f"{cmd.get('subdominator_cmd')}",
        f"{result_dir}/.logs/s_stdout",
        f"{result_dir}/.logs/s_stderr"
    ),
    (
        "subfinder",
        f"{cmd.get('subfinder_cmd')}",
        f"{result_dir}/.logs/s_stdout",
        f"{result_dir}/.logs/s_stderr"
    ),
    (
        "cero",
        f"{cmd.get('cero_cmd')}",
        f"{result_dir}/.logs/_stdout",
        f"{result_dir}/.logs/_stderr"
    ),
    (
        "sublist3r",
        f"{cmd.get('sublist3r_cmd')}",
        f"{result_dir}/.logs/stdout",
        f"{result_dir}/.logs/stderr"
    ),
    (
        "yass",
        f"{cmd.get('yass_cmd')}",
        f"{result_dir}/.logs/_stdout",
        f"{result_dir}/.logs/_stderr"
    ),
    (
        "githubsubdomains",
        f"{cmd.get('githubsubdomains_cmd')}",
        f"{result_dir}/.logs/stdout",
        f"{result_dir}/.logs/stderr"
    ),
    (
        "gitlabsubdomains",
        f"{cmd.get('gitlabsubdomains_cmd')}",
        f"{result_dir}/.logs/_stdout",
        f"{result_dir}/.logs/_stderr"
    )
]

# Filter commands based on selected tools
commands = [cmd for cmd in all_commands if cmd[0] in selected_tools]

# Execute selected commands
print(commands)