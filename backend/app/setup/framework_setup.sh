# Initialization

if [ "$EUID" -eq 0 ] && [ -n "$SUDO_USER" ]; then
    REAL_USER="$SUDO_USER"
    REAL_HOME=$(eval echo "~$SUDO_USER")
else
    REAL_USER="$USER"
    REAL_HOME="$HOME"
fi


MAIN_DIR="$REAL_HOME/projectrecon"
BACKEND_DIR="$REAL_HOME/projectrecon/projectrecon"
FRONTEND_DIR="$REAL_HOME/projectrecon/pentest-dashboard"
PSQL_USER="postgres_pr"
PSQL_PASSWORD="psqlnotsafe123"
PSQL_DB="project_recon"
DESKTOP_FILE="$REAL_HOME/.local/share/applications/projectrecon.desktop"
PYTHON_ENV="$REAL_HOME/.projectrecon_env"

# Check for internet connectivity using ping
echo "[INFO] Checking internet connectivity..."
if ! ping -c 1 1.1.1.1 &> /dev/null; then
    echo "[ERROR] No internet connection detected. Please connect to the internet and re-run the script."
    exit 1
fi

# Update and install system requirements
if command -v apt &> /dev/null; then
    PKG_MGR="apt"
    UPDATE_CMD="sudo apt update -y && sudo apt upgrade -y"
    DEPS="git npm tmux python3 python3-pip gcc python3-dev libpq-dev postgresql postgresql-contrib curl"
    REMOVE="python3-urllib3 python3-typing-extensions"
elif command -v dnf &> /dev/null; then
    PKG_MGR="dnf"
    UPDATE_CMD="sudo dnf upgrade -y"
    DEPS="git npm tmux python3 python3-pip gcc python3-devel libpq-devel postgresql postgresql-server curl"
    REMOVE=""  # no matching packages
elif command -v pacman &> /dev/null; then
    PKG_MGR="pacman"
    UPDATE_CMD="sudo pacman -Syu --noconfirm"
    DEPS="git npm tmux python python-pip gcc libpq postgresql curl"
    REMOVE=""  # no matching packages
else
    echo "[ERROR] Unsupported Linux distribution."
    exit 1
fi

echo "[+] Updating system..."
eval "$UPDATE_CMD"

echo "[+] Installing dependencies..."
sudo $PKG_MGR install -y $DEPS

if [[ -n "$REMOVE" ]]; then
    echo "[+] Removing unnecessary packages..."
    sudo $PKG_MGR remove -y $REMOVE || true
fi


# Activate python environment
python3 -m venv "$PYTHON_ENV"
source "$PYTHON_ENV"/bin/activate

# Clone github repo for both frontend and backend
echo "[+] Cloning repositories..."
if [[ -d "$MAIN_DIR" ]]; then
    rm -rf "$MAIN_DIR" > /dev/null 2>&1
fi
mkdir -p "$MAIN_DIR" && cd "$MAIN_DIR"
git clone https://github.com/shivpratapsingh111/pentest-dashboard &
git clone https://github.com/shivpratapsingh111/projectrecon &
wait

# Setup Frontend
echo "[+] Setting up framework..."
sudo npm install -g vite
cd pentest-dashboard && npm install

# Install backend requirements
cd ../projectrecon
pip3 install -r requirements.txt

# Install and setup PostgreSQL
echo "[+] Starting PostgreSQL service..."
sudo systemctl enable postgresql
sudo systemctl start postgresql
echo "[+] Creating PostgreSQL user "$PSQL_USER" with password..."
sudo -u postgres psql -c "CREATE USER $PSQL_USER WITH SUPERUSER PASSWORD "$PSQL_PASSWORD";"
echo "[+] Configuring PostgreSQL to allow remote password authentication..."


# Setup Postgresql
if [[ "$PKG_MGR" == "apt" ]]; then
    PG_HBA="/etc/postgresql/$(ls /etc/postgresql)/main/pg_hba.conf"
    PG_CONF="/etc/postgresql/$(ls /etc/postgresql)/main/postgresql.conf"

elif [[ "$PKG_MGR" == "dnf" ]]; then
    PG_HBA="/var/lib/pgsql/data/pg_hba.conf"
    PG_CONF="/var/lib/pgsql/data/postgresql.conf"

    # If default location doesn't exist, look for versioned directories
    if [[ ! -f "$PG_HBA" || ! -f "$PG_CONF" ]]; then
        for dir in /var/lib/pgsql/*/data; do
            if [[ -f "$dir/pg_hba.conf" && -f "$dir/postgresql.conf" ]]; then
                PG_HBA="$dir/pg_hba.conf"
                PG_CONF="$dir/postgresql.conf"
                break
            fi
        done
    fi

    sudo postgresql-setup --initdb

elif [[ "$PKG_MGR" == "pacman" ]]; then
    PG_HBA="/var/lib/postgres/data/pg_hba.conf"
    PG_CONF="/var/lib/postgres/data/postgresql.conf"
    sudo -u postgres initdb -D /var/lib/postgres/data
fi

if [[ -f "$PG_HBA" && -f "$PG_CONF" ]]; then
    echo "[INFO] Updating pg_hba.conf and postgresql.conf..."

    sudo sed -i "s/^host *all *all *127.0.0.1\/32 *.*$/host all all 0.0.0.0\/0 md5/" "$PG_HBA"
    sudo sed -i "s/^#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"

    echo "[INFO] Restarting PostgreSQL..."

    sudo systemctl restart postgresql
else
    echo "[ERROR] Could not find pg_hba.conf or postgresql.conf"
    exit 1
fi

echo "[✅] PostgreSQL setup complete!"

# Setup TMUX with custom aliases
if [[ "$(basename "$SHELL")" == "bash" ]]; then
cat << 'EOF' >> $REAL_HOME/.bashrc

# TMUX aliases
function tns() {
    tmux new-session -s "$1"
}
function ta() {
    tmux attach -t "$1"
}
function tks() {
    tmux kill-session -t "$1"
}
alias tls='tmux list-sessions'

# Project environment
export PYTHONPATH="\$PYTHONPATH:\$BACKEND_DIR"
source $HOME/projectrecon_env/bin/activate

EOF

# Get public IP and set it up for frontend
PUBLIC_IP=$(curl -s ifconfig.me)
cat << EOF > "$FRONTEND_DIR/.env"
VITE_APP_BASE_URL="http://$PUBLIC_IP:54755"
VITE_APP_BASE_WEBSOCKET="ws://$PUBLIC_IP:54755"
EOF

# Setup DB config for backend
cat << EOF > "$BACKEND_DIR/backend/app/config/db_config.py"
DB_CONFIG = {
    'dbname': '$PSQL_DB',
    'user': '$PSQL_USER',
    'password': '$PSQL_PASSWORD',
    'host': 'localhost'
}
EOF

# Setup TMUX for zsh with custom aliases
elif [[ "$(basename "$SHELL")" == "zsh" ]]; then
cat << 'EOF' >> $REAL_HOME/.zshrc

# TMUX aliases
function tns() {
    tmux new-session -s "$1"
}
function ta() {
    tmux attach -t "$1"
}
function tks() {
    tmux kill-session -t "$1"
}
alias tls='tmux list-sessions'

# Project environment
export PYTHONPATH="\$PYTHONPATH:\$BACKEND_DIR"
source $HOME/projectrecon_env/bin/activate

EOF

# Get public IP and set it up for frontend
PUBLIC_IP=$(curl -s ifconfig.me)
cat << EOF > "$FRONTEND_DIR/.env"
VITE_APP_BASE_URL="http://$PUBLIC_IP:54755"
VITE_APP_BASE_WEBSOCKET="ws://$PUBLIC_IP:54755"
EOF

# Setup DB config for backend
cat << EOF > "$BACKEND_DIR/backend/app/config/db_config.py"
DB_CONFIG = {
    'dbname': '$PSQL_DB',
    'user': '$PSQL_USER',
    'password': '$PSQL_PASSWORD',
    'host': 'localhost'
}
EOF

else
    echo "Neither Bash nor Zsh is detected as the default shell. Please change your shell to one of these"
fi 

# Notify
echo "Project Recon Setup Completed"

bash tool_install_setup.sh

# Making Desktop entry
mkdir -p "$(dirname "$DESKTOP_FILE")"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=ProjectRecon
Comment=Launch ProjectRecon Framework
Exec=$BACKEND_DIR/start.py
Icon=$BACKEND_DIR/backend/app/setup/icon.png
Type=Application
Categories=Utility;
EOF

chmod +x "$DESKTOP_FILE"
echo "Desktop entry created at $DESKTOP_FILE"

# Notify
echo "Tool Setup Completed"
echo "To run this framework, search for 'ProjectRecon' in your system application and click on the icon"