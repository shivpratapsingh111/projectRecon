from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.pyscripts.process_manager import start_tool
from app.config.config  import *
import os, re, requests, subprocess


def func_urls_ps(target_name, domain_list):
    print("Executing: func_urls_ps")
    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{target_name}/{domain}/urls"
        domain_dir = f"{root_Data_Dir}/{target_name}/{domain}"
        os.makedirs(result_dir, exist_ok=True) # Making a directory for each domain passed as targets
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(start_tool, target_name, "waybackurls", f"cat {domain_dir}/subdomains/{subdomainResults} | waybackurls", f"{result_dir}/{waybackurls_Passive_UrlResults}"),
                executor.submit(start_tool, target_name, "gau", f"cat {domain_dir}/subdomains/{subdomainResults} | gau", f"{result_dir}/{gau_Passive_UrlResults}"),
                executor.submit(start_tool, target_name, "waymore", f"waymore -n -xwm -urlr 0 -r 2 -i {domain} -mode U -oU {result_dir}/{waymore_Passive_UrlResults}", f"{result_dir}/waymore2from_start_tool_func"),
            ]
            for future in futures:  # Ensure all tasks in the first set are completed
                future.result()
        print(f"Passive URL Enum completed for {domain}")
        command = f"cat {result_dir}/{waybackurls_Passive_UrlResults} {result_dir}/{gau_Passive_UrlResults} {result_dir}/{waymore_Passive_UrlResults} | sort -u >> {result_dir}/{passive_CombinedUrlResults}" # Combining passive results
        with open(f"{root_Data_Dir}/{target_name}/{central_log_file}" , "a") as writeLog:
            process = subprocess.Popen(
                command,
                # stdout=writeLog,
                stderr=writeLog,
                shell=True,
            )
            process.wait()
        print("Passive URLs Combined")

def func_urls_ac(target_name, domain_list):
    print("Executing: func_urls_ac")
    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{target_name}/{domain}/urls"
        domain_dir = f"{root_Data_Dir}/{target_name}/{domain}"
        os.makedirs(result_dir, exist_ok=True) # Making a directory for each domain passed as targets
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(start_tool, target_name, "katana", f"katana -u {domain_dir}/subdomains/{subdomainResults} -o {result_dir}/{katana_Active_UrlResults} -silent -hl -nc -d 5 -aff -retry 2 -iqp -c 20 -p 20 -xhr -jc -kf -ef css,jpg,jpeg,png,svg,img,gif,mp4,flv,ogv,webm,webp,mov,mp3,m4a,m4p,scss,tif,tiff,ttf,otf,woff,woff2,bmp,ico,eot,htc,rtf,swf,image", f"{result_dir}/katana2from_start_tool_func"),
                executor.submit(start_tool, target_name, "hakrawler", f"cat {domain_dir}/subdomains/{subdomainResults} | hakrawler -d 5 -insecure -subs -t 40", f"{result_dir}/{hakrawler_Active_UrlResults}"),
            ]
            for future in futures:  # Ensure all tasks in the first set are completed
                future.result()
        print(f"Active URL Enum completed for {domain}")
        command = f"cat {result_dir}/{katana_Active_UrlResults} {result_dir}/{hakrawler_Active_UrlResults} | sort -u >> {result_dir}/{active_CombinedUrlResults}" # Combining passive results
        with open(f"{root_Data_Dir}/{target_name}/{central_log_file}" , "a") as writeLog:
            process = subprocess.Popen(
                command,
                # stdout=writeLog,
                stderr=writeLog,
                shell=True,
            )
            process.wait()
        print("Active URLs Combined")

def arrangeUrls(urls_path, urlsArranged200_path, urlsArrangedAll_path):

    extensions = ["~", "7z", "ace", "action", "aliases", "arc", "arj", "asc", "aws/config", "aws/credentials", "babelrc", "backup", "bak", "bas", "bash", "bash_profile", "bashrc", "bat", "bin", "bk", "bkp", "blade", "build", "buildignore", "buildpath", "bz", "bz2", "bzrconfig", "bzrignore", "c", "c++", "c$", "cab", "cache", "cc", "cer", "cfg", "cfignore", "cgi", "circleci", "class", "cls", "cnf", "commitlintrc", "conf", "config", "cpio", "cpp", "cpp$", "cred", "credentials", "crt", "cs", "cs^", "csh", "csr", "csv", "csvignore", "ctl", "ctp", "cxx", "dat", "data", "db", "db3", "deb", "der", "dir", "dist", "dll", "dmg", "dmp", "do", "dob", "docker", "docker-compose.yaml", "docker-compose.yml", "dockerfile", "dockerignore", "dockerrc", "docx", "DS_Store", "ear", "editorconfig", "ejs", "ejs^", "eml", "env", "env.development", "env.local", "env.production", "env.test", "erb", "eslintignore", "eslintrc", "exe", "factories", "fish", "freemarker", "frm", "ftl", "functions", "git", "gitattributes", "gitignore", "gitmodules", "go", "gpg", "gradle", "gz", "h", "h++", "haml", "handlebars", "hbs", "helmfile", "helmignore", "hgignore", "hgrc", "hh", "hjson", "hqx", "htaccess", "htmllintrc", "htpasswd", "huskyrc", "hxx", "idea", "ignore", "img", "inc", "inf", "ini", "iso", "jade", "jar", "java", "jenkinsfile", "jks", "jnlp", "json5", "jsx", "kbdx", "kdb", "kdbx", "key", "keychain", "ksh", "kube/config", "lck", "ldf", "less", "lintstagedrc", "lock", "log", "lst", "lz", "lzh", "lzma", "lzo", "m2", "markdown", "markdownlint", "md", "mdf", "mdx", "mercurial-hgignore", "metadata", "mkd", "mkdown", "msg", "mustache", "mvn", "mysql", "mysql-connect", "netrc", "npmignore", "npmrc", "nrg", "nunjucks", "nz", "old", "openvpn", "orig", "ost", "out", "ova", "ovpn", "p12", "p7b", "p7c", "pak", "pea", "pem", "pfx", "pgp", "pgsql", "php3", "php4", "php5", "php7", "pid", "pkcs12", "pkg", "pl", "pm", "pom", "ppdf", "ppk", "pptx", "prefs", "prettierrc", "profile", "project", "properties", "ps1", "pst", "ptxt", "pug", "pwd", "pxml", "py", "pyc", "pyd", "pyo", "pyx", "rake", "rar", "raw", "rb", "rc", "renv", "rhtml", "ron", "rpm", "rs", "rspec", "rst", "rsx", "ru", "s7z", "sar", "sass", "save", "sea", "secrets", "settings", "sfx", "sh", "sit", "sitx", "slugignore", "sm", "smx", "sql", "sqlite", "sqlite3", "styl", "stylelintrc", "swap", "swm", "swo", "swp", "tag.gz", "tar", "tar.bz2", "tar.gz", "tar.gz.xz", "tar.xz", "tar.xz.gz", "tbz2", "tcsh", "temp", "terraformrc", "test", "tfignore", "tgz", "tlz", "tmp", "todo", "toml", "tpl", "travis.yml", "ts", "tsx", "twig", "uue", "vb", "vbproj", "vbs", "vm", "vmdk", "vs", "vscode", "vtl", "vue", "war", "watchmanconfig", "webconfig", "webinfo", "webproj", "wim", "wsgi", "xar", "xlsx", "xmi", "xsql", "xz", "yaml", "yarnrc", "yml", "Z", "zip", "zoo", "zsh", "zshrc", "txt"]

    def check_url(url):
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            return url, response.status_code == 200
        except requests.RequestException:
            return url, False

    def process_extension(ext, urls, urlsArranged200_path, urlsArrangedAll_path):
        arranged_urls = [url.strip() for url in urls if re.search(rf"\.{ext}(\?.*)?$", url, re.IGNORECASE)]
        if arranged_urls:
            with open(urlsArranged200_path, 'a') as file200, open(urlsArrangedAll_path, 'a') as fileAll:
                fileAll.write(f"================(.{ext})\n\n")
                for url in arranged_urls:
                    url, is_200 = check_url(url)
                    if is_200:
                        file200.write(f"{url}\n")
                    fileAll.write(f"{url}\n")
                fileAll.write("\n\n")

    with open(urls_path, 'r') as urls_file:
        urls = urls_file.readlines()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_extension, ext, urls, urlsArranged200_path, urlsArrangedAll_path) for ext in extensions]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing extension: {e}")

def organise_urls(target_name,domain_list):
    for domain in domain_list:
        print(f"Organising URL Enum for {domain}")
        result_dir = f"{root_Data_Dir}/{target_name}/{domain}/urls"
        command = f"""cat {result_dir}/{passive_CombinedUrlResults} {result_dir}/{active_CombinedUrlResults} | sort -u >> {result_dir}/{urlResults}"""
        with open(f"{root_Data_Dir}/{target_name}/{central_log_file}" , "a") as writeLog:
            process = subprocess.Popen(
                command,
                # stdout=writeLog,
                stderr=writeLog,
                shell=True,
            )
        command = f"""cat {result_dir}/{urlResults} | grep -F .js | cut -d "?" -f 1 | sort -u >> {result_dir}/{jsUrls}"""
        with open(f"{root_Data_Dir}/{target_name}/{central_log_file}" , "a") as writeLog:
            process = subprocess.Popen(
                command,
                # stdout=writeLog,
                stderr=writeLog,
                shell=True,
            )
            process.wait()
        arrangeUrls(f"{result_dir}/{urlResults}", f"{result_dir}/{urlsArranged200}", f"{result_dir}/{urlsArrangedAll}")



def func_urls_both(target_name, domain_list):
    func_urls_ac(target_name, domain_list)
    func_urls_ps(target_name, domain_list)
    organise_urls(target_name,domain_list)