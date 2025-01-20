import argparse
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.config.config import *
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)

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

def arrangeUrls_small(urls_path, urlsArranged200_path):

    extensions_small = ["~", "7z", "aws/config", "aws/credentials", "babelrc", "backup", "bak", "bash", "bash_profile", "bashrc", "bat", "bin", "bk", "bkp", "build", "buildignore", "buildpath", "bz", "bz2", "cache", "cgi", "class", "conf", "config", "crt", "csv", "csvignore", "ctl", "dat", "data", "db", "db3", "deb", "der", "dist", "dll", "dmg", "dmp", "docker", "docker-compose.yaml", "docker-compose.yml", "dockerfile", "dockerignore", "dockerrc", "docx", "DS_Store", "ejs", "eml", "env", "env.development", "env.local", "env.production", "env.test", "eslintignore", "eslintrc", "exe", "git", "gitattributes", "gitignore", "gitmodules", "go", "gpg", "gradle", "gz", "haml", "helmfile", "helmignore", "hgignore", "hgrc", "hjson", "hqx", "htaccess", "htmllintrc", "htpasswd", "huskyrc", "ignore", "img", "inc", "inf", "ini", "iso", "jar", "java", "jenkinsfile", "jks", "json5", "jsx", "key", "keychain", "kube/config", "lck", "less", "lintstagedrc", "lock", "log", "markdown", "markdownlint", "md", "metadata", "mvn", "mysql", "mysql-connect", "netrc", "npmignore", "npmrc", "nrg", "old", "openvpn", "out", "ova", "ovpn", "pak", "pem", "pgp", "pgsql", "php3", "php4", "php5", "php7", "pid", "pkcs12", "pkg", "pl", "ppdf", "pptx", "prefs", "profile", "project", "properties", "ps1", "pwd", "pxml", "py", "pyc", "pyd", "pyo", "pyx", "rar", "raw", "rb", "rc", "renv", "rhtml", "save", "secrets", "settings", "sh", "sql", "sqlite", "sqlite3", "styl", "stylelintrc", "swap", "swm", "swo", "swp", "tag.gz", "tar", "tar.bz2", "tar.gz", "tar.gz.xz", "tar.xz", "tar.xz.gz", "tbz2", "tcsh", "temp", "terraformrc", "test", "tfignore", "tgz", "tlz", "tmp", "todo", "toml", "tpl", "travis.yml", "ts", "tsx", "twig", "vb", "vbproj", "vbs", "vm", "vmdk", "vs", "vscode", "vtl", "vue", "war", "watchmanconfig", "webconfig", "webinfo", "webproj", "wim", "wsgi", "xar", "xlsx", "xsql", "xz", "yaml", "yarnrc", "yml", "zip", "zsh", "zshrc", "txt"]
    
    def process_extension(ext, urls, urlsArranged200_path):
        arranged_urls = [url.strip() for url in urls if re.search(rf"\.{ext}(\?.*)?$", url, re.IGNORECASE)]
        if arranged_urls:
            with open(urlsArranged200_path, 'a') as file200:
                file200.write(f"================(.{ext})\n\n")
                for url in arranged_urls:
                    file200.write(f"{url}\n")
                file200.write("\n\n")

    with open(urls_path, 'r') as urls_file:
        urls = urls_file.readlines()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_extension, ext, urls, urlsArranged200_path) for ext in extensions_small]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing extension: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arrange URLs by extensions and filter HTTP 200 responses.")
    parser.add_argument("urls_path", type=str, help="Path to the file containing URLs.")
    parser.add_argument("urlsArranged200_path", type=str, help="Path to the output file for HTTP 200 URLs.")
    parser.add_argument("urlsArrangedAll_path", type=str, help="Path to the output file for all processed URLs.")

    args = parser.parse_args()

    arrangeUrls(args.urls_path, args.urlsArranged200_path, args.urlsArrangedAll_path)
    logger.debug("Urls arranged big")
    arrangeUrls_small(urlsArranged200, urlsArranged200_small)
    logger.debug("Urls arranged small")
