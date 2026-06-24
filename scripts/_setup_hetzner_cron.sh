#!/bin/bash
# BKS Hetzner — Setup automatico cron per price monitor + batch
# Eseguire su Hetzner: bash scripts/_setup_hetzner_cron.sh
# Server: 95.217.232.186

set -e

BKS_DIR="/opt/bks"
VENV="$BKS_DIR/venv"
PYTHON="$VENV/bin/python"

echo "=== BKS Hetzner Automation Setup ==="
echo "Server: $(hostname)"
echo "Dir: $BKS_DIR"

# 1. Installa dipendenze Python
echo ""
echo "1. Installa dipendenze..."
apt-get update -qq && apt-get install -y -qq python3 python3-pip python3-venv

# 2. Setup venv
if [ ! -d "$VENV" ]; then
    python3 -m venv "$VENV"
fi
$VENV/bin/pip install -q requests aiohttp urllib3 openai

# 3. Sincronizza codice (da eseguire dopo rsync da locale)
mkdir -p "$BKS_DIR"
echo "   Code dir: $BKS_DIR"

# 4. Crea systemd service per price monitor
cat > /etc/systemd/system/bks-price-monitor.service << 'EOF'
[Unit]
Description=BKS Price Monitor — Shopify price audit and fix
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/opt/bks
ExecStart=/opt/bks/venv/bin/python /opt/bks/scripts/_price_monitor.py
StandardOutput=journal
StandardError=journal
SyslogIdentifier=bks-price-monitor

[Install]
WantedBy=multi-user.target
EOF

# 5. Crea systemd timer (ogni 6 ore)
cat > /etc/systemd/system/bks-price-monitor.timer << 'EOF'
[Unit]
Description=BKS Price Monitor — ogni 6 ore
Requires=bks-price-monitor.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=6h
Persistent=true

[Install]
WantedBy=timers.target
EOF

# 6. Crea service per batch design (on-demand)
cat > /etc/systemd/system/bks-design-batch.service << 'EOF'
[Unit]
Description=BKS Design Batch — Printify 200 prodotti
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/opt/bks
ExecStart=/opt/bks/venv/bin/python /opt/bks/scripts/_production_pipeline.py --workers 2 --resume
StandardOutput=journal
StandardError=journal
SyslogIdentifier=bks-design-batch
TimeoutStartSec=7200

[Install]
WantedBy=multi-user.target
EOF

# 7. Crea timer GMC sync giornaliero (se esiste script)
cat > /etc/systemd/system/bks-gmc-sync.service << 'EOF'
[Unit]
Description=BKS GMC Daily Sync
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/opt/bks
ExecStart=/opt/bks/venv/bin/python /opt/bks/scripts/gmc_daily_sync.py
StandardOutput=journal
StandardError=journal
SyslogIdentifier=bks-gmc-sync
EOF

cat > /etc/systemd/system/bks-gmc-sync.timer << 'EOF'
[Unit]
Description=BKS GMC Sync — ogni giorno alle 07:00 CET
Requires=bks-gmc-sync.service

[Timer]
OnCalendar=*-*-* 06:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# 8. Enable e start timers
systemctl daemon-reload
systemctl enable bks-price-monitor.timer
systemctl start bks-price-monitor.timer
systemctl enable bks-gmc-sync.timer
systemctl start bks-gmc-sync.timer

echo ""
echo "=== SETUP COMPLETATO ==="
echo ""
echo "Timer attivi:"
systemctl list-timers --all | grep bks
echo ""
echo "Comandi utili:"
echo "  systemctl start bks-price-monitor       # run price fix ora"
echo "  systemctl start bks-design-batch        # run batch design ora"
echo "  journalctl -u bks-price-monitor -f      # log price monitor"
echo "  journalctl -u bks-design-batch -f       # log design batch"
echo "  systemctl status bks-price-monitor.timer"
