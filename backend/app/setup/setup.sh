#!/bin/bash

export DEBIAN_FRONTEND=noninteractive
allTools=("assetfinder" "gf" "bbot" "getjs" "github-subdomains" "gitlab-subdomains" "sublist3r" "cero" "yass" "dnsresolver" "jsluice" "unfurl" "hakrawler" "ffuf" "subjs" "massdns" "fetcher" "subfinder" "amass" "subdominator" "haktrails" "waymore" "katana" "gau" "waybackurls" "nuclei" "kxss" "qsreplace" "dirsearch" "httpx" "dnsgen" "altdns" "alterx" "puredns")

commonUtilties=("python3" "python3-pip" "sed" "gawk" "coreutils" "curl" "git" "jq" "net-tools" "tmux" "unzip" "zip" "dnsutils" "nmap")

missingTools=()
missingAgain=()
packetManager=""
allPresent=0

mkdir -p ~/tools


installmissingTools(){

    for tool in ${missingTools[@]}; do
        
        case $tool in

        # Subdomain gathering tools
            "amass")
                /usr/local/go/bin/go install -v github.com/owasp-amass/amass/v4/...@master
                ;;
            "assetfinder")
                /usr/local/go/bin/go install -v github.com/tomnomnom/assetfinder@latest
                ;;
            "haktrails")
                /usr/local/go/bin/go install -v github.com/hakluke/haktrails@latest
                ;;
            "subdominator")
                pip install --upgrade subdominator
                ;;
            "subfinder")
                /usr/local/go/bin/go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
                ;;
            "dnsgen")
                pip3 install dnsgen
                ;;
            "altdns")
                pip3 install "py-altdns"
                ;;
            "alterx")
                /usr/local/go/bin/go install github.com/projectdiscovery/alterx/cmd/alterx@latest
                ;;
            "puredns")
                /usr/local/go/bin/go install github.com/d3mondev/puredns/v2@latest
                ;;
            "massdns")
                git clone https://github.com/blechschmidt/massdns.git /tmp/massdns && cd /tmp/massdns && make && mv bin/massdns /usr/local/bin/ && cd ../ && rm -rf massdns
                ;;
            "dnsresolver")
                git clone https://github.com/ethicalhackingplayground/dnsresolver ~/tools/dnsresolver && cd ~/tools/dnsresolver && echo | cargo install --path .
                ;;
            "ffuf")
                /usr/local/go/bin/go install github.com/ffuf/ffuf/v2@latest
                ;;
            "bbot")
                pip3 install bbot
                ;;
            "github-subdomains")
                /usr/local/go/bin/go install github.com/gwen001/github-subdomains@latest
                ;;
            "gitlab-subdomains")
                /usr/local/go/bin/go install github.com/gwen001/gitlab-subdomains@latest
                ;;
            "yass")
                git clone https://github.com/shivpratapsingh111/yass.git ~/tools/yass && cd ~/tools/yass && pip3 install .
                ;;
            "cero")
                /usr/local/go/bin/go install github.com/glebarez/cero@latest
                ;;
            "sublist3r")
                git clone https://github.com/aboul3la/Sublist3r ~/tools/Sublist3r
                ;;


        # URL gathering tools
            "gau")
                /usr/local/go/bin/go install -v github.com/lc/gau/v2/cmd/gau@latest
                ;;
            "katana")
                /usr/local/go/bin/go install -v github.com/projectdiscovery/katana/cmd/katana@latest 
                ;;
            "waybackurls")
                /usr/local/go/bin/go install -v github.com/tomnomnom/waybackurls@latest
                ;;
            "waymore")
                pip3 install git+https://github.com/xnl-h4ck3r/waymore.git
                ;;
            "hakrawler")
                /usr/local/go/bin/go install -v github.com/hakluke/hakrawler@latest
                ;;
            "getjs")
                /usr/local/go/bin/go install github.com/003random/getJS/v2@latest
                ;;

        # Misc Tools
            "dirsearch")
                pip3 install dirsearch
                ;;
            "tld")
                pip3 install tld
                ;;
            "kxss")
                /usr/local/go/bin/go install -v github.com/Emoe/kxss@latest
                ;;
            "nuclei")
                /usr/local/go/bin/go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
                ;;
            "qsreplace")
                /usr/local/go/bin/go install -v github.com/tomnomnom/qsreplace@latest
                ;;
            "httpx")
                /usr/local/go/bin/go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
                ;;
            "fetcher")
                /usr/local/go/bin/go install -v github.com/shivpratapsingh111/fetcher@latest
                ;;
            "unfurl")
                /usr/local/go/bin/go install -v github.com/tomnomnom/unfurl@latest
                ;;
            "subjs")
                /usr/local/go/bin/go install -v github.com/lc/subjs@latest
                ;;
            "gf")
                /usr/local/go/bin/go install -v github.com/tomnomnom/gf@latest && git clone https://github.com/tomnomnom/gf /tmp/gf && mv /tmp/gf/examples ~/.gf
                ;;
            "gfpatterns")
                git clone https://github.com/shivpratapsingh111/gfpatterns /tmp/gfpatterns && mkdir -p ~/.gf && mv /tmp/gfpatterns/done/* ~/.gf && mv ~/.gf/extensions/* ~/.gf/ && rm -rf ~/.gf/extensions
                ;;
            "jsluice")
                /usr/local/go/bin/go install github.com/BishopFox/jsluice/cmd/jsluice@latest
                ;;
            *)
                echo "[+] Installation method not added for: $tool"
                ;;
        esac
    done

    if [ $(ls ~/go/bin | wc -l) -gt 0 ]; then
        sudo mv ~/go/bin/* /usr/bin/
    fi
}





fixMissingAgain(){
    for tool in ${missingAgain[@]}; do
        echo "[+] Fixing misses"
        sudo pip3 uninstall -y $tool
        echo "[+] Fixed misses"
    done

    installmissingTools
}





checkTools() {
    # Define tool list
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
        echo "[+] The following tools are missing:"
        echo "---"
        for tool in "${missingTools[@]}"; do
            echo "- $tool"
        done
        echo "---"
        echo ""
        installmissingTools

    fi


# Checking and fixing errors for still missing tools (that may not got installed due to some errors)
    for tool in "${allTools[@]}"; do
    
        if ! command -v $tool &>/dev/null; then
            missingAgain+="$tool"
        fi
    done

    if [ ${#missingAgain[@]} -gt 0 ]; then
        fixMissingAgain
    fi


# Checking if all tools are installed
    for tool in "${allTools[@]}"; do
    
        if ! command -v $tool &>/dev/null; then
            allPresent+=1
        fi
    done

    if [[ $allPresent -gt 0 ]]; then
        echo
    else
        echo "[+] All required tools are installed"
        echo "[+] Set API keys in config file for waymore & subfinder"
        echo -e "[+] Run below command to change timezone if you are using a VPS:\nsudo timedatectl set-timezone Asia/Kolkata"
    fi

# Printing name of tools, that were unable to install
    for tool in "${allTools[@]}"; do
    
        if ! command -v $tool &>/dev/null; then
            echo "[+] Not Installed, Install manually $tool"
            echo "[+] Don't forget to set API keys in config file for waymore & subfinder"
            echo -e "[+] Run below command to change timezone if you are using a VPS:\nsudo timedatectl set-timezone Asia/Kolkata"
            
        fi
    done

}




updateUpgrade() {

        pip3 install colorama


    if [ -f /etc/debian_version ]; then

        isDebian=1

        echo "[+] OS: Debian"
        
        sudo apt update -y
        sudo apt full-upgrade -y
        sudo apt autoremove -y
        sudo apt install dnsutils -y

        sudo apt install -y curl build-essential
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source $HOME/.cargo/env


        # apt install -y python3-pip && echo "[+] Python Installed" || echo "[+] Python Not Installed" | tee -a log.txt
        # apt install -y python3.11-venv && echo "[+] Python venv Installed" || echo "[+] Python venv not Installed" | tee -a log.txt
        # dir=$(pwd)
        # cd ~ && echo "[+] Dir changed to '~'" || echo "[+] Dir didn't changed to '~'" | tee -a log.txt
        # python3 -m venv .venvPython && echo "[+] Python vevnv made" || echo "[+] Python vevnv not made  " | tee -a log.txt
        # source .venvPython/bin/activate && echo "[+] Python vevnv activated" || echo "[+] Python venv not activated" | tee -a log.txt
        # cd $dir  && echo "[+] Directory changed to $dir" || echo "[+] Directory not changed to $dir" | tee -a log.txt
#        echo "#!/bin/bash" >> ~/.activatePythonVenv.sh
#        echo "source ~/.venvPython/bin/activate" >> ~/.activatePythonVenv.sh
#        chmod +x ~/.activatePythonVenv.sh





        for utility in ${commonUtilties[@]}; do

            if [ $utility == "coreutils" ]; then

                if ! command -v cut &>/dev/null; then

                    echo "[+] $utility not present, Installing..."
                    sudo apt install coreutils -y

                fi
            
            elif [ $utility == "dnsutils" ]; then
            
                if ! command -v cut &>/dev/null; then

                    echo "[+] $utility not present, Installing..."
                    sudo apt install dnsutils -y

                fi

            elif ! command -v $utility &>/dev/null; then

                echo "[+] $utility not present, Installing..."
                sudo apt install $utility -y

            fi
            
        done

        # Install Chrome for screenshoting subdomains using nuclei templates
        cd /tmp 
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        apt install -y ./google-chrome-stable_current_amd64.deb

    elif [ -f /etc/fedora-release ]; then

        echo "[+] OS: Fedora"

        sudo dnf update -y
        sudo dnf clean all -y
        sudo dnf install dnsutils -y

        sudo dnf install -y curl make gcc
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
        source $HOME/.cargo/env


        for utility in ${commonUtilties[@]}; do

            if [ $utility == "coreutils" ]; then

                if ! command -v cut &>/dev/null; then

                    echo "[+] $utility not present, Installing..."
                    sudo dnf install coreutils -y

                fi
            
            elif [ $utility == "dnsutils" ]; then
            
                if ! command -v cut &>/dev/null; then

                    echo "[+] $utility not present, Installing..."
                    sudo dnf install dnsutils -y

                fi

            elif ! command -v $utility &>/dev/null; then

                echo "[+] $utility not present, Installing..."
                sudo dnf install $utility -y

            fi

        done

         # Install Chrome for screenshoting subdomains using nuclei templates
        cd /tmp
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
        yum localinstall -y google-chrome-stable_current_x86_64.rpm



    elif [ -f /etc/arch-release ]; then

        echo "[+] OS: Arch"

        sudo pacman -Syu
        sudo pacman -S dnsutils -y

        sudo pacman -S --needed curl base-devel
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
        source $HOME/.cargo/env


        for utility in ${commonUtilties[@]}; do

            if [ $utility == "coreutils" ]; then

                if ! command -v cut &>/dev/null; then

                    echo "[+] $utility not present, Installing..."
                    pacman -S coreutils

                fi

            elif [ $utility == "dnsutils" ]; then
            
                if ! command -v cut &>/dev/null; then

                    echo "[+] $utility not present, Installing..."
                    pacman -S dnsutils

                fi

            elif ! command -v $utility &>/dev/null; then

                echo "[+] $utility not present, Installing..."
                pacman -S $utility

            fi
            
        done  

    fi

# Installing resolvers for Puredns from trickest
    if ! [ -f '~/.config/puredns/resolvers.txt' ]; then
        mkdir -p ~/.config/puredns
        wget "https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt" 1> /dev/null
        wait
        mv resolvers.txt ~/.config/puredns/resolvers.txt
    fi
    

    
# Checking & Installing Go Lang
 
    if ! command -v /usr/local/go/bin/go &> /dev/null; then
        echo "Go is not installed. Installing..."
        curl https://go.dev/dl/go1.22.3.linux-amd64.tar.gz -L --output go1.22.3.linux-amd64.tar.gz &
        wait
        sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.22.3.linux-amd64.tar.gz & 
        wait
        rm go1.22.3.linux-amd64.tar.gz
    fi

    if [ "$(echo $SHELL)" = "/bin/bash" ]; then
        echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.bashrc
    elif [ "$(echo $SHELL)" = "/bin/zsh" ]; then
        echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.zshrc
    else
        echo "Neither Bash nor Zsh is detected as the default shell. Please change your shell to one of these"
    fi 

}



# Driver Code
mainFunction(){
if [ "$EUID" -ne 0 ]
  then echo "Please run $0 as root"
  exit
fi

# activate python env if not activated

VENV_PATH=~/python_environment
ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"

# Check if the virtual environment exists
if [[ ! -f "$ACTIVATE_SCRIPT" ]]; then
    echo "Virtual environment not found at $VENV_PATH. Creating..."
    python3 -m venv "$VENV_PATH"
    echo "Virtual environment created."
fi

# Check if the virtual environment is already activated
if [[ "$VIRTUAL_ENV" != "$VENV_PATH" ]]; then
    echo "Activating virtual environment..."
    source "$ACTIVATE_SCRIPT"
else
    echo "Virtual environment is already active."
fi

# Confirm activation (Optional)
if [[ "$VIRTUAL_ENV" == "$VENV_PATH" ]]; then
    echo "Virtual environment activated successfully."
else
    echo "Failed to activate virtual environment."
fi


updateUpgrade
rm $(which httpx)
checkTools

if [[ $isDebian -eq 1 ]]; then
    clear
    echo "[+] All required tools are installed"
    echo "[+] Set API keys in config file for waymore & subfinder"
    echo -e "[+] Run below command to change timezone if you are using a VPS:\nsudo timedatectl set-timezone Asia/Kolkata"
    if [ "$(echo $SHELL)" = "/bin/bash" ]; then
        echo -e "[+] Please log out and log in again, or use below command:\nsource ~/.bashrc"
    elif [ "$(echo $SHELL)" = "/bin/zsh" ]; then
        echo -e "[+] Please log out and log in again, or use below command:\nsource ~/.zshrc"
    else
        echo "Neither Bash nor Zsh is detected as the default shell. Please change your shell to one of these"
    fi 
fi
}


# ===========================================[Code Runs from here]

projectReconSetup
mainFunction