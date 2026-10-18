#!/usr/bin/env bash
# ==============================================================================
# PrintMaster A4 - One-Click Ubuntu/Debian VPS Deployment Script
# Automatically sets up Python, virtualenv, dependencies, and systemd service.
# ==============================================================================

set -e

echo "🚀 Starting PrintMaster A4 Telegram Bot Deployment..."

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="printmaster-bot"
CURRENT_USER=$(whoami)

echo "📁 Application Directory: $APP_DIR"
echo "👤 Service User: $CURRENT_USER"

# 1. Update and install prerequisites
echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 2. Setup Virtual Environment
if [ ! -d "$APP_DIR/venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv "$APP_DIR/venv"
fi

echo "📥 Installing Python requirements..."
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# 3. Create required directories
mkdir -p "$APP_DIR/data" "$APP_DIR/temp_uploads"

# 4. Create Systemd Service for 24/7 background operation & auto-restart
echo "⚙️ Configuring systemd service..."

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=PrintMaster A4 Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$APP_DIR/..
ExecStart=$APP_DIR/venv/bin/python -m telegram_bot.bot
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# 5. Reload systemd, enable and start service
echo "🔄 Enabling and starting $SERVICE_NAME..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo ""
echo "=================================================================="
echo "🎉 PrintMaster A4 Bot is now running 24/7 on your server!"
echo "=================================================================="
echo "Useful commands:"
echo "• View live logs:     sudo journalctl -u $SERVICE_NAME -f"
echo "• Restart the bot:    sudo systemctl restart $SERVICE_NAME"
echo "• Stop the bot:       sudo systemctl stop $SERVICE_NAME"
echo "• Service status:     sudo systemctl status $SERVICE_NAME"
echo "=================================================================="
