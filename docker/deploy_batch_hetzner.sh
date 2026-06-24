#!/bin/bash
# Deploy e lancia batch design su Hetzner (95.217.232.186)
# Uso locale: bash docker/deploy_batch_hetzner.sh [--test N] [--collection pulse]

HETZNER="95.217.232.186"
SSH_USER="${BKS_SSH_USER:-root}"
REMOTE_DIR="/opt/bks-batch"
ARGS="${@:---resume}"

echo "=== BKS Batch Deploy → Hetzner $HETZNER ==="

# 1. Sync file necessari (no dati pesanti, solo scripts + skills)
echo "Sync scripts e skill..."
rsync -avz --exclude='*.pyc' --exclude='__pycache__' \
  --exclude='*.csv' --exclude='wonder_*.jpg' \
  scripts/ $SSH_USER@$HETZNER:$REMOTE_DIR/scripts/
rsync -avz BKS_SKILL/ $SSH_USER@$HETZNER:$REMOTE_DIR/BKS_SKILL/
rsync -avz ecommerce_automation/ $SSH_USER@$HETZNER:$REMOTE_DIR/ecommerce_automation/
rsync -az .env $SSH_USER@$HETZNER:$REMOTE_DIR/.env

# 2. Sync Dockerfile
rsync -az docker/Dockerfile.batch $SSH_USER@$HETZNER:$REMOTE_DIR/Dockerfile

# 3. Build & run container su Hetzner
echo "Build container su Hetzner..."
ssh $SSH_USER@$HETZNER bash -s << EOF
  cd $REMOTE_DIR
  docker build -t bks-batch -f Dockerfile .
  docker rm -f bks-batch-run 2>/dev/null || true
  docker run -d --name bks-batch-run \
    --restart unless-stopped \
    -v $REMOTE_DIR/ecommerce_automation:/app/ecommerce_automation \
    bks-batch $ARGS
  echo "Container avviato:"
  docker logs --tail 20 bks-batch-run
EOF

echo ""
echo "Monitor: ssh $SSH_USER@$HETZNER 'docker logs -f bks-batch-run'"
echo "Stop:    ssh $SSH_USER@$HETZNER 'docker stop bks-batch-run'"
echo "Log:     $REMOTE_DIR/ecommerce_automation/design_batch_log.json"
