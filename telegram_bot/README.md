# 🖨️ PrintMaster A4 — Telegram Bot

> **Image Duplicator & Poster Maker** — A feature-complete Telegram bot port of the PrintMaster A4 desktop application, offering a simple yet gorgeous interactive interface for photo duplication, sticker printing, poster tiling, and print-ready PDF/image exports.

---

## ✨ Features & Parity with Desktop App

| Desktop Feature | Telegram Bot Equivalent | Status |
| :--- | :--- | :---: |
| **Duplicator Mode** | Full grid layout on standard A4 (Portrait / Landscape) | ✅ |
| **Poster Mode** | Split large images across multiple A4 tiles (2×2, 3×3, 4×4, custom) | ✅ |
| **Live Visual Preview** | Real-time realistic A4 sheet preview with drop shadow & guides sent to chat | ✅ |
| **Standard Photo Presets** | Passport (3.5×4.5cm), US Visa (5.1×5.1cm), Business Card, ID Badge, A6, A5, Polaroid | ✅ |
| **Quick Grid Presets** | 1-Up, 2-Up, 4-Up, 6-Up, 8-Up, 9-Up, 12-Up, 16-Up, 24-Up | ✅ |
| **Custom Dimensions** | Adjust Width & Height in cm/mm, Aspect Ratio lock/unlock | ✅ |
| **Spacing / Gap** | 0 mm, 1 mm, 2 mm, 3 mm, 5 mm, 10 mm, or custom mm | ✅ |
| **Page Margins** | Normal (10mm), Narrow (5mm), Borderless (0mm), Wide (20mm), or Custom | ✅ |
| **Print Margin Guide Line** | Visual printable boundary guide toggle | ✅ |
| **Cut Marks** | 3.5 mm corner tick lines & dashed cutting boundary for scissor trimming | ✅ |
| **Image Borders** | Colored border (Black, Gray, White, Red) with thickness (0.2 - 2.0 mm) | ✅ |
| **Auto-Rotate 90°** | Automatically calculates if rotating yields more copies per sheet | ✅ |
| **Alignment** | Center on sheet vs. Top-Left alignment | ✅ |
| **Batch Multi-Sheet Export** | Set total copies (20, 50, 100, 200, 500, or custom) to span multiple A4 pages | ✅ |
| **Poster Overlap & Glue Guides**| Configurable overlap (0–20 mm) with dashed glue line markers and sheet indexes | ✅ |
| **Vector PDF Export** | True point-scale (72 pt/inch) multi-page PDF document ready for standard printers | ✅ |
| **300 DPI Export** | Ultra crisp 2480 × 3508 px PNG image export for photo labs | ✅ |
| **Beginner Interactive Tutorial** | Step-by-step interactive 6-step walkthrough (`/tutorial`) with FAQ & glossary | ✅ |
| **User Tracking & Admin Dashboard** | Track who used the bot, count interactions/uploads/PDFs, export CSV reports (`/admin`, `/stats`) | ✅ |

---

## 👑 Owner & Admin Analytics (`/admin` or `/stats`)

Want to know who used your bot, how many times it was used, and what features they ran?

Send `/admin` or `/stats` in Telegram to open the **Admin Dashboard**:
- 👥 **Total Registered Users:** Exact count of unique users who ever started or interacted with the bot.
- 📊 **Total Actions / Interactions:** Total commands, button taps, and inputs.
- ⚡ **Active Users:** Unique active users in the last 24 hours and last 7 days.
- 📁 **Detailed Breakdown:**
  - 🖼 Images uploaded
  - 📄 Vector PDFs generated
  - 🎨 300 DPI Images exported
- 🏆 **Top Users Ranking:** Ordered list of most active users with usernames (`@username`), total actions, upload counts, and last seen timestamps.
- 📜 **Recent Activity Stream:** Real-time chronological audit trail of the last user actions.
- 📥 **Export Users CSV:** Downloads a complete spreadsheet (`PrintMaster_Users_Analytics.csv`) with all user profiles and metrics.

> **🔒 Restricting Admin Access:**
> Add your Telegram User ID to `.env`:
> ```env
> ADMIN_ID=123456789
> ```
> *(If `ADMIN_ID` is not yet set, the bot will show your ID on the screen when you type `/admin` so you can copy and paste it into `.env` effortlessly!)*

---

## 🐣 Beginner Tutorial & Printing Guide

New to printing or using the bot? Use the `/tutorial` command or tap **📚 Beginner Tutorial** in the chat menu anytime!

### 🎯 5 Golden Rules for Printing at Home:
1. **Send as File / Document for Best Quality:** Telegram compresses normal photos. Sending as a *Document* keeps 100% original sharpness.
2. **Always Print at 100% (Actual Size):** In your printer software, **never select "Fit to Page"** or "Shrink to Fit". Always choose **"Actual Size" / "100%"** so passport photos and cards maintain exact millimeter dimensions.
3. **Use Cut Marks (✂️):** Corner tick marks guarantee straight scissor or craft knife cuts every time.
4. **Use Poster Mode for Big Wall Art:** Choose **2×2** (~A2 size) or **3×3** (~A0 size) to print posters across multiple A4 sheets. The bot prints overlap glue lines ("*Glue Sheet #2 Here*") and sheet numbers for simple assembly!
5. **Practice with the Demo:** Don't have a photo? Tap **🧪 Try Demo Image** to practice immediately with the included sample sticker!

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

Install dependencies (if not already installed):
```bash
pip install -r telegram_bot/requirements.txt
```

### 2. Configure Your Telegram Bot Token
1. Open Telegram and talk to [@BotFather](https://t.me/BotFather) to create a new bot (e.g., `/newbot`).
2. Copy your bot API token.
3. Open `telegram_bot/.env` and paste your token:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
   ```

### 3. Launch the Bot Locally
On Windows, simply double-click `run_bot.bat` or run:
```bash
python -m telegram_bot.bot
```

### 4. Host 24/7 on the Internet (Cloud & VPS)
Want to host the bot permanently online? See the complete guide:
👉 **[HOSTING_GUIDE.md](HOSTING_GUIDE.md)** for 1-click deployments:
- **Railway / Render.com:** 5-minute cloud background worker setup via GitHub.
- **Ubuntu/Debian VPS:** 1-click auto-installer script (`deploy_vps.sh`) with auto-restarts on reboot.
- **Docker Compose:** Run `docker compose up -d` on any server.

---

## 📱 How to Use in Telegram

1. **Start the Bot:** Send `/start` to receive the welcome message and load the interactive control center.
2. **Learn with the Tutorial:** Send `/tutorial` or tap **📚 Beginner Tutorial** for a step-by-step tour.
3. **Send Any Image:**
   - Send any photo or uncompressed image file (PNG, JPG, WEBP).
   - The bot immediately generates a live A4 preview with your current layout settings.
4. **Customize Layout:**
   - Tap **📐 Size Presets** to select standard sizes like Passport or Business Card.
   - Tap **📊 Quick Grids** for instant 2×2, 3×2, or 4×4 arrangements.
   - Tap **🔀 Mode** to switch between **Duplicator** (multiple copies on 1 sheet) and **Poster Maker** (tiled wall poster).
   - Tap **✂️ Cuts & Borders** to toggle cutting tick marks, border colors, auto-rotation, or sheet alignment.
   - Tap **📦 Batch Export** to print 50, 100, or 200 copies across multiple A4 pages.
5. **Export Output:**
   - Tap **📄 Export PDF** to receive a print-ready vector PDF file with exact millimeter scaling.
   - Tap **🖼 Export 300 DPI** to receive an uncompressed high-resolution raster image.

---

## 🏗️ Architecture & Project Structure

```
telegram_bot/
├── bot.py             # Main entry point & polling runner
├── config.py          # Environment settings & asset path configuration
├── models.py          # Session state dataclass (user state persistence)
├── layout_engine.py   # Coordinate calculations, grid fitting & poster tiling math
├── renderer.py        # Pillow canvas renderer for live preview & 300 DPI exports
├── pdf_exporter.py    # ReportLab vector PDF generator
├── keyboards.py       # Inline keyboard builders for Telegram UI
├── handlers.py        # Telegram event handlers (commands, photos, callbacks)
├── database.py        # SQLite tracking, user analytics & CSV reporting
├── tutorial.py        # Step-by-step beginner tutorial, FAQ, and glossary
├── data/              # SQLite database storage (printmaster.db)
├── test_engine.py     # Local verification test script
├── run_bot.bat        # Windows one-click local launcher
├── Dockerfile         # Production container definition
├── docker-compose.yml # 1-command container orchestration
├── Procfile           # Cloud PaaS worker definition (Render, Railway)
├── deploy_vps.sh      # 1-click Ubuntu/Debian systemd VPS installer
├── HOSTING_GUIDE.md   # Complete guide for hosting online 24/7
├── requirements.txt   # Python dependencies
├── .env.example       # Example environment configuration
└── .env               # Active environment file for bot token
```

---

## 👨‍💻 Credits & Contact
- **Original App:** PrintMaster A4 (Image Duplicator & Poster Maker)
- **Developer:** [aitadz.pro](https://aitadz.pro)
- **Telegram:** [@aitadz](https://t.me/aitadz)
- **Facebook:** [aitadz.pro](https://www.facebook.com/aitadz.pro)
- **WhatsApp:** [+213 558 655 085](https://wa.me/213558655085)
