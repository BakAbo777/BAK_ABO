#!/bin/bash
# BKS Dashboard — Setup su Hetzner (Ubuntu 22.04)
# Esegui come root: bash hetzner_dashboard_setup.sh

set -e

REPO="https://github.com/BakAbo777/BAK_ABO.git"
INSTALL_DIR="/opt/bks-dashboard"
SERVICE_USER="root"
PORT="8501"
DOMAIN="dashboard.bakabo.club"

echo "=== BKS Dashboard Setup ==="

# 1. Dipendenze sistema
apt-get update -qq
apt-get install -y python3-venv python3-pip nginx certbot python3-certbot-nginx git

# 2. Clone repo
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "→ Aggiornamento repo esistente..."
    cd "$INSTALL_DIR" && git pull origin main
else
    echo "→ Clone repo..."
    git clone "$REPO" "$INSTALL_DIR"
fi

# 3. Python venv + dipendenze
cd "$INSTALL_DIR"
python3 -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt flask

# 4. Streamlit config
mkdir -p "$INSTALL_DIR/.streamlit"
cat > "$INSTALL_DIR/.streamlit/config.toml" << 'EOF'
[server]
port = 8501
address = "127.0.0.1"
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
EOF

# 5. Systemd service
cat > /etc/systemd/system/bks-dashboard.service << EOF
[Unit]
Description=BKS Studio Dashboard (Streamlit)
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/.venv/bin/python -m streamlit run streamlit_master.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/bks-dashboard.log
StandardError=append:/var/log/bks-dashboard.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable bks-dashboard
systemctl start bks-dashboard

# 6. Nginx config con basic auth
echo "→ Password nginx (da impostare manualmente):"
echo "    htpasswd -c /etc/nginx/.htpasswd roberto"

cat > /etc/nginx/sites-available/bks-dashboard << EOF
server {
    listen 80;
    server_name $DOMAIN;

    auth_basic "BKS Studio";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400;
    }
}
EOF

ln -sf /etc/nginx/sites-available/bks-dashboard /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo ""
echo "=== Setup completato ==="
echo "1. Copia .env: scp 'I:/BAK ABO/.env' root@95.217.232.186:$INSTALL_DIR/.env"
echo "2. Imposta password: htpasswd -c /etc/nginx/.htpasswd roberto"
echo "3. SSL: certbot --nginx -d $DOMAIN"
echo "4. DNS: A record dashboard.bakabo.club → 95.217.232.186"
echo "5. Verifica: systemctl status bks-dashboard"
