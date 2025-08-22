checkTools() {
    # Define tool list
    allTools=("assetfinder" "gf" "bbot" "getJS" "github-subdomains" "gitlab-subdomains" "sublist3r" "cero" "yass" "dnsresolver" "jsluice" "unfurl" "hakrawler" "ffuf" "subjs" "massdns" "fetcher" "subfinder" "amass" "subdominator" "haktrails" "waymore" "katana" "gau" "waybackurls" "nuclei" "kxss" "qsreplace" "dirsearch" "httpx" "dnsgen" "altdns" "alterx" "puredns")
    missingTools=()

    for tool in "${allTools[@]}"; do
        case "$tool" in
            sublist3r)
                if ! python3 ~/tools/Sublist3r/sublist3r.py &>/dev/null; then
                    missingTools+=("$tool")
                fi
                ;;
            *)
                if ! command -v "$tool" &>/dev/null; then
                    missingTools+=("$tool")
                fi
                ;;
        esac
    done

    if [ ${#missingTools[@]} -gt 0 ]; then
        IFS=','  # Set comma as delimiter
        echo "${missingTools[*]}"
        unset IFS  # Reset IFS to default
    else
        echo "[+] All tools are present."
    fi
}

# Run check
checkTools
