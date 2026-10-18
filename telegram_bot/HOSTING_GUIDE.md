# 🌐 How to Host & Launch PrintMaster A4 on the Internet (24/7)

This guide shows you the best, easiest ways to deploy and host your Telegram bot online so it runs **24/7** without needing your computer to stay on.

---

## ⚡ Quick Comparison: Which Hosting Option Should You Choose?

| Platform | Difficulty | Cost | Recommended For |
| :--- | :---: | :---: | :--- |
| **Railway** | 🟢 Very Easy | Free trial / ~$5 mo | Quickest 5-minute setup with GitHub |
| **Render.com** | 🟢 Very Easy | Free tier / $7 mo | Great 1-click cloud background worker |
| **Linux VPS (Ubuntu)** | 🟡 Easy | $3–$4 mo (or Free on Oracle) | **Best overall** — 100% control & permanent database persistence |
| **Docker (Any VPS)** | 🟢 Very Easy | Included with VPS | 1 command: `docker compose up -d` |
| **PythonAnywhere** | 🟡 Easy | Free tier | Quick Python-focused hosting |

---

## 🚀 Method 1: Railway (Easiest 5-Minute Cloud Deploy)

Railway is one of the smoothest platforms for hosting Python Telegram bots.

### Steps:
1. **Upload your code to GitHub:**
   - Create a new private repository on [GitHub](https://github.com).
   - Push your project code to GitHub.
2. **Connect to Railway:**
   - Go to [railway.app](https://railway.app) and sign in with your GitHub account.
   - Click **"New Project"** → **"Deploy from GitHub repo"**.
   - Select your repository.
3. **Configure Environment Variables:**
   - In Railway, click on your project service → go to the **"Variables"** tab.
   - Add your variables:
     - `TELEGRAM_BOT_TOKEN` = `your_token_from_botfather`
     - `ADMIN_ID` = `your_telegram_user_id` (optional)
4. **Deploy:**
   - Railway automatically detects `requirements.txt` and `Procfile`.
   - Click **Deploy**. Your bot is now live on the internet 24/7!
   - You can view real-time logs directly in the Railway dashboard.

---

## 🚀 Method 2: Render.com (Background Worker)

Render provides reliable cloud hosting with automatic GitHub deployments.

### Steps:
1. Go to [render.com](https://render.com) and create an account.
2. In the Render dashboard, click **"New +"** and select **"Background Worker"** (Note: Telegram bots run long polling, so select *Background Worker*, not Web Service).
3. Connect your GitHub repository.
4. Fill in the service details:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r telegram_bot/requirements.txt`
   - **Start Command:** `python -m telegram_bot.bot`
5. Click **"Advanced"** → **"Add Environment Variable"**:
   - `TELEGRAM_BOT_TOKEN` = `your_token`
   - `ADMIN_ID` = `your_id`
6. Click **"Create Background Worker"**. Render will build and launch your bot automatically!

---

## 🐧 Method 3: Linux VPS (Ubuntu / Debian) — Recommended for Full Persistence

A cheap Linux Virtual Private Server (VPS) from **Hetzner** (~$3.50/mo), **DigitalOcean** ($4/mo), **Linode**, or **Oracle Cloud Always-Free Tier** is the most professional and cost-effective choice. It keeps your SQLite database permanently intact.

We have included a 1-click auto-installer script [`deploy_vps.sh`](deploy_vps.sh).

### Steps:
1. **Connect to your VPS via SSH:**
   ```bash
   ssh root@YOUR_SERVER_IP
   ```

2. **Upload or clone your project:**
   ```bash
   git clone <YOUR_REPO_URL> /opt/printmaster
   cd /opt/printmaster
   ```
   *(Or copy the folder using SCP / FileZilla)*.

3. **Configure your `.env` file:**
   ```bash
   nano telegram_bot/.env
   ```
   Paste your token:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ADMIN_ID=your_telegram_user_id
   ```
   Save with `Ctrl+O` and exit with `Ctrl+X`.

4. **Run the One-Click Deployment Script:**
   ```bash
   chmod +x telegram_bot/deploy_vps.sh
   ./telegram_bot/deploy_vps.sh
   ```

### What this script does automatically:
- Installs Python 3, pip, and virtual environment tools.
- Sets up an isolated Python virtual environment (`venv`).
- Installs all dependencies.
- Configures a **Systemd Service** (`printmaster-bot.service`) so the bot:
  - Runs in the background 24/7.
  - Automatically restarts if it ever crashes.
  - Automatically starts on server reboot.

### Managing your bot on VPS:
```bash
# Check status
sudo systemctl status printmaster-bot

# Watch real-time logs
sudo journalctl -u printmaster-bot -f

# Restart bot
sudo systemctl restart printmaster-bot

# Stop bot
sudo systemctl stop printmaster-bot
```

---

## 🐳 Method 4: Docker & Docker Compose

If you have Docker installed on your server or computer, you can run the bot with a single command.

1. Ensure [`telegram_bot/.env`](.env) contains your `TELEGRAM_BOT_TOKEN`.
2. Open terminal in the `telegram_bot` directory and run:
   ```bash
   docker compose up -d --build
   ```

3. **Check running status:**
   ```bash
   docker compose ps
   ```

4. **View live logs:**
   ```bash
   docker compose logs -f
   ```

5. **Stop the bot:**
   ```bash
   docker compose down
   ```

The `docker-compose.yml` mounts the `./data` volume automatically, so all your user statistics and tracking database are permanently preserved on the host machine.

---

## 🐍 Method 5: PythonAnywhere

1. Create a free or paid account at [pythonanywhere.com](https://www.pythonanywhere.com).
2. Open the **"Consoles"** tab and start a **Bash Console**.
3. Clone your repository:
   ```bash
   git clone <YOUR_REPO_URL>
   cd <YOUR_REPO_DIR>
   ```
4. Create virtual environment and install requirements:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r telegram_bot/requirements.txt
   ```
5. Go to the **"Tasks"** tab on PythonAnywhere and create an **"Always-on Task"**:
   - Command: `/home/yourusername/<YOUR_REPO_DIR>/venv/bin/python -m telegram_bot.bot`
6. Click **Save** and start the task.

---

## 🛡️ Security Checklist for Production

- [ ] **Keep `.env` private:** Never commit `.env` containing your real bot token to a public GitHub repository. Use a private repository.
- [ ] **Set `ADMIN_ID`:** Set your Telegram User ID in `.env` so only you can access `/admin` and `/stats`.
- [ ] **Data Backup:** Back up `telegram_bot/data/printmaster.db` periodically if you want to archive your user stats.
