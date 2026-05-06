# ════════════════════════════════════════════════════════════════════
#  Dockerfile — بوت تيليجرام لتحميل الوسائط
#  يبني صورة Docker قابلة للنشر على أي سيرفر يدعم Docker
# ════════════════════════════════════════════════════════════════════

# ─── المرحلة الأولى: البناء ──────────────────────────────────────────
FROM python:3.11-slim AS builder

# تثبيت أدوات البناء المطلوبة لـ curl-cffi
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libffi-dev \
        libssl-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# إنشاء البيئة الافتراضية داخل الصورة
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# نسخ ملف المتطلبات وتثبيتها
COPY bot/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt


# ─── المرحلة الثانية: الصورة النهائية (أصغر حجماً) ──────────────────
FROM python:3.11-slim

# تثبيت ffmpeg لدمج الصوت والفيديو في yt-dlp
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# استيراد البيئة الافتراضية من مرحلة البناء
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# ─── إعداد مجلد العمل ────────────────────────────────────────────────
WORKDIR /app

# نسخ ملفات البوت
COPY bot/ ./bot/

# ─── متغيرات البيئة الافتراضية (القيم تُعاد من .env أو docker-compose) ─
ENV BOT_TOKEN=""
ENV ADMIN_ID=""
ENV WEBHOOK_URL=""
ENV WEBHOOK_PORT="8443"
ENV WEBHOOK_SECRET=""
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ─── البورت الداخلي لـ Webhook ───────────────────────────────────────
# يُستخدم فقط في وضع Webhook — يتجاهله البوت عند Polling
EXPOSE 8443

# ─── تشغيل البوت ─────────────────────────────────────────────────────
WORKDIR /app/bot
CMD ["python", "main.py"]
