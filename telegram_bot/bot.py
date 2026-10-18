"""
PrintMaster A4 - Telegram Bot Main Application
Run this file to start the Telegram bot.
"""

import sys
import logging

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from pathlib import Path

# Ensure parent directory is in sys.path so package imports work from any CWD
_current_dir = Path(__file__).resolve().parent
_parent_dir = _current_dir.parent
for _p in (str(_parent_dir), str(_current_dir)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from telegram_bot.config import BOT_TOKEN
from telegram_bot.handlers import (
    start_command,
    help_command,
    tutorial_command,
    admin_command,
    handle_photo_upload,
    handle_callback_query,
    handle_text_input,
)

import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("PrintMasterBot")


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Responds to cloud provider health check pings (e.g. Render Free Web Service)."""
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"PrintMaster A4 Telegram Bot is alive and running!")

    def log_message(self, format, *args):
        pass  # Suppress HTTP access logs to keep bot console clean


def start_health_check_server():
    """Starts a minimal HTTP server if the cloud environment defines a PORT (e.g. Render/Heroku)."""
    port_str = os.environ.get("PORT", "").strip()
    if port_str and port_str.isdigit():
        port = int(port_str)
        try:
            server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            logger.info(f"🌐 Cloud health-check HTTP server listening on port {port}")
        except Exception as e:
            logger.warning(f"Could not bind health-check server on port {port}: {e}")


def main():
    if not BOT_TOKEN:
        print("\n" + "=" * 60)
        print("⚠️  TELEGRAM_BOT_TOKEN IS NOT SET!")
        print("=" * 60)
        print("To run the bot, please provide your bot token:")
        print("1. Open 'telegram_bot/.env' (or create it)")
        print("2. Add your token from @BotFather:")
        print("   TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ")
        print("3. Run the bot again.")
        print("=" * 60 + "\n")
        sys.exit(1)

    print("🚀 Starting PrintMaster A4 Telegram Bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("tutorial", tutorial_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("stats", admin_command))
    app.add_handler(CommandHandler("cancel", handle_text_input))

    # Photo and Image Documents
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_upload))
    app.add_handler(
        MessageHandler(
            filters.Document.IMAGE | filters.Document.MimeType("image/png") | filters.Document.MimeType("image/jpeg") | filters.Document.MimeType("image/webp"),
            handle_photo_upload,
        )
    )

    # Inline Keyboards
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    # Text Input (dimensions, numbers, etc.)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    # Start cloud health check server if PORT is provided by host (e.g. Render Web Service)
    start_health_check_server()

    print("✅ PrintMaster A4 Bot is active and listening for messages!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
