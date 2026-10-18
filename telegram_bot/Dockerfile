FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output for real-time logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (for Pillow and ReportLab font rendering if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libfreetype6-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app/telegram_bot/

# Create data and uploads directories
RUN mkdir -p /app/telegram_bot/data /app/telegram_bot/temp_uploads

# Start the bot
CMD ["python", "-m", "telegram_bot.bot"]
