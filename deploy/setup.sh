#!/bin/bash
# First-time VPS setup for drug target explorer.
# Run on the VPS as root or with sudo.
set -e

echo "=== Drug Target Explorer — VPS Setup ==="

# 1. Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    echo "Docker installed."
else
    echo "Docker already installed."
fi

# 2. Ensure docker compose plugin is available
if ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose plugin not found. Install it manually."
    exit 1
fi

# 3. Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.production.example .env
    echo ""
    echo ">>> IMPORTANT: Edit .env and set a strong NEO4J_PASSWORD <<<"
    echo "    nano .env"
    echo ""
    echo "Then run: docker compose up -d"
else
    echo ".env already exists."
    echo ""
    echo "Ready to launch: docker compose up -d"
fi

echo ""
echo "=== DNS Reminder ==="
echo "Add an A record at your DNS provider:"
echo "  bio.arcosdiaz.com → $(curl -s ifconfig.me || echo '<your-vps-ip>')"
echo ""
echo "Caddy will auto-provision the SSL certificate once DNS propagates."
