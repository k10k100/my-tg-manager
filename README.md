# 🤖 بوت تيليجرام — تحميل الوسائط متعدد المنصات

بوت تيليجرام متكامل مبني بـ Python يدعم تحميل الفيديوهات والصور من **9 منصات** مختلفة، مع نظام نقاط وإحالات وVIP ودفع بـ Telegram Stars ولوحة إدارة React.

---

## ✨ المميزات

| الميزة | التفاصيل |
|--------|----------|
| 📥 **9 منصات** | YouTube, Instagram, TikTok, Twitter/X, Facebook, Pinterest, Snapchat, LinkedIn, Dailymotion |
| 🎁 **نظام الإحالات** | كل إحالة = 50 نقطة تُضاف تلقائياً |
| 👑 **نظام VIP** | تحميل بلا حدود + أولوية + بدون إعلانات |
| 💳 **Telegram Stars** | دفع مباشر داخل التطبيق لشراء النقاط |
| 📢 **إدارة الإعلانات** | مستخدمون يُرسلون إعلانات للموافقة عليها |
| 📡 **البث المجدول** | إرسال رسائل لجميع المستخدمين بتوقيت محدد |
| 🛡️ **الحماية** | Rate Limit + طابور تحميل + حد يومي |
| ⚙️ **لوحة أدمن** | واجهة React عربية RTL متكاملة |

---

## 📋 المتطلبات

- Python **3.11** أو أحدث
- حساب تيليجرام + توكن بوت من [@BotFather](https://t.me/BotFather)
- Node.js **18+** (للوحة الإدارة فقط)

---

## 🚀 التثبيت والتشغيل

### الخطوة 1 — استنساخ المستودع

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### الخطوة 2 — إنشاء بيئة بايثون افتراضية

```bash
# إنشاء البيئة الافتراضية
python3 -m venv venv

# تفعيلها على Linux / macOS
source venv/bin/activate

# تفعيلها على Windows
venv\Scripts\activate
```

### الخطوة 3 — تثبيت المكتبات

```bash
pip install -r bot/requirements.txt
```

### الخطوة 4 — إعداد متغيرات البيئة

```bash
# انسخ ملف المثال
cp .env.example .env

# افتح .env وضع القيم الحقيقية
nano .env   # أو أي محرر نصوص
```

محتوى ملف `.env`:

```env
BOT_TOKEN=123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_ID=123456789
SESSION_SECRET=any-long-random-string-here
```

> **كيف أجد ADMIN_ID؟** أرسل أي رسالة لـ [@userinfobot](https://t.me/userinfobot) على تيليجرام.

### الخطوة 5 — تشغيل البوت

```bash
cd bot
python main.py
```

يجب أن ترى:

```
INFO - البوت يعمل...
INFO - ⏰ حلقة الجدولة تعمل في الخلفية
```

---

## ⚙️ الإعدادات (config.json)

يمكن تعديل جميع الإعدادات من لوحة الأدمن أو مباشرةً في `bot/config.json`:

| المفتاح | الوصف | الافتراضي |
|---------|--------|-----------|
| `download_limit_free` | الحد اليومي للمستخدم العادي | 5 |
| `download_limit_vip` | الحد اليومي لـ VIP (-1 = بلا حدود) | -1 |
| `vip_cost_points` | تكلفة VIP بالنقاط | 500 |
| `points_per_referral` | نقاط لكل إحالة | 50 |
| `max_file_size_mb` | أقصى حجم ملف | 50 |
| `rate_limit_enabled` | تفعيل الحماية من الإغراق | true |
| `rate_limit_max` | أقصى طلبات في الفترة | 2 |
| `rate_limit_cooldown` | مدة الانتظار بالثواني | 60 |

---

## 📁 هيكل المشروع

```
bot/
├── main.py                  # نقطة الدخول الرئيسية
├── config.json              # إعدادات البوت
├── channels.json            # قنوات الاشتراك الإجباري
├── packages.json            # باقات الدفع بـ Stars
├── requirements.txt         # مكتبات Python
└── modules/
    ├── downloader.py        # محرك التحميل الرئيسي (9 منصات)
    ├── tiktok_dl.py         # تحميل TikTok (سلسلة fallback متعددة)
    ├── admin.py             # لوحة تحكم الأدمن (2100+ سطر)
    ├── users.py             # إدارة المستخدمين والنقاط والـ VIP
    ├── subscription.py      # نظام الاشتراك الإجباري في القنوات
    ├── payments.py          # دفع Telegram Stars
    ├── referrals.py         # نظام الإحالات
    ├── store.py             # المتجر (شراء VIP بالنقاط)
    ├── ads.py               # إدارة الإعلانات
    ├── analytics.py         # تحليلات الاستخدام
    ├── scheduler.py         # جدولة البث الجماعي
    ├── protection.py        # Rate Limit + طابور التحميل
    ├── messages.py          # رسائل ديناميكية واقتباسات
    ├── packages.py          # إدارة باقات Stars
    └── roles.py             # صلاحيات الأدمن الفرعيين

artifacts/
├── admin-panel/             # لوحة الإدارة (React + Vite)
└── api-server/              # API Server (Node.js + Express)
```

---

## 🔧 تشغيل لوحة الإدارة (اختياري)

```bash
# تثبيت pnpm إذا لم يكن مثبتاً
npm install -g pnpm

# تثبيت التبعيات
pnpm install

# تشغيل لوحة الإدارة
pnpm --filter @workspace/admin-panel run dev

# تشغيل API Server
pnpm --filter @workspace/api-server run dev
```

ثم افتح المتصفح على: `http://localhost:PORT/admin-panel`

---

## 📢 إعداد قنوات الاشتراك الإجباري

من لوحة الأدمن في تيليجرام (⚙️ الأدمن ← القنوات):
1. أضف البوت كمشرف في القناة
2. أدخل معرّف القناة (مثال: `@mychannel`)
3. حدد اسمها وهل هي مفعّلة

---

## 💳 إعداد Telegram Stars

1. اذهب لـ @BotFather → Bot Settings → Payments
2. فعّل Telegram Stars
3. أضف الباقات من لوحة الأدمن ← الباقات

---

## 🗄️ قاعدة البيانات PostgreSQL (اختياري)

البوت يعمل **بدون قاعدة بيانات** باستخدام ملفات JSON. عندما تنمو قاعدة مستخدميك أو تحتاج لأداء أفضل، فعّل PostgreSQL بأمر واحد.

| | JSON (الافتراضي) | PostgreSQL |
|---|---|---|
| **الإعداد** | فوري — لا شيء | يحتاج DATABASE_URL |
| **الأداء** | جيد لـ < 10,000 مستخدم | ممتاز لأي حجم |
| **الأمان** | ملفات محلية | حماية كاملة + ACID |
| **النسخ الاحتياطي** | نسخ الملفات يدوياً | `pg_dump` تلقائي |
| **التبديل** | تلقائي عبر DATABASE_URL | — |

### تفعيل PostgreSQL مع Docker

```bash
# 1. أضف كلمة السر في .env
echo "DB_PASSWORD=كلمة_سر_قوية" >> .env
echo "DATABASE_URL=postgresql://botuser:كلمة_سر_قوية@postgres/botdb" >> .env

# 2. شغّل البوت مع قاعدة البيانات
docker compose --profile db up -d

# 3. (مرة واحدة فقط) انقل بياناتك الموجودة من JSON إلى DB
docker compose exec bot python migrate_json_to_db.py
```

### استخدام قاعدة بيانات خارجية (Supabase / Railway / Neon)

```bash
# ضع رابط الاتصال في .env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

البوت يكتشف قاعدة البيانات تلقائياً ويبدّل إليها دون تعديل أي كود.

---

## 🔗 وضع Webhook مقابل Polling

| | Polling | Webhook |
|---|---|---|
| **متى تستخدمه** | تطوير محلي، Replit | إنتاج على VPS |
| **HTTPS مطلوب** | لا | نعم |
| **نطاق مطلوب** | لا | نعم |
| **الكفاءة** | جيد | ممتاز (أسرع + أقل استهلاكاً) |
| **الإعداد** | تلقائي | يحتاج nginx + SSL |

**التبديل بينهما تلقائي:** إذا كان `WEBHOOK_URL` فارغاً في `.env` → Polling. إذا كان مضبوطاً → Webhook.

---

## 🐳 النشر بـ Docker (الأسرع والأنظف)

> **متطلب:** تثبيت [Docker](https://docs.docker.com/get-docker/) و [Docker Compose](https://docs.docker.com/compose/install/) على السيرفر.

### وضع A — Polling (الأبسط، بدون نطاق)

```bash
# 1. جهّز البيئة
cp .env.example .env
nano .env      # ضع BOT_TOKEN و ADMIN_ID فقط — اتركْ WEBHOOK_URL فارغاً

# 2. شغّل
docker compose up -d

# 3. تابع
docker compose logs -f bot
```

البوت سيكتشف أن `WEBHOOK_URL` فارغ ويعمل تلقائياً بوضع Polling.

---

### وضع B — Webhook (للإنتاج الاحترافي)

**المتطلبات:** نطاق حقيقي يشير لـ IP السيرفر + البورتان 80 و 443 مفتوحان.

#### الطريقة السريعة (سكريبت تلقائي)

```bash
# 1. جهّز البيئة
cp .env.example .env
nano .env      # ضع BOT_TOKEN و ADMIN_ID

# 2. شغّل السكريبت (يضبط nginx + SSL + البوت بأمر واحد)
sudo ./nginx/setup-ssl.sh bot.example.com your@email.com
```

السكريبت يفعل كل شيء: يضبط nginx، يستخرج شهادة Let's Encrypt، يحدّث `.env`، ويشغّل البوت.

#### الطريقة اليدوية (خطوة بخطوة)

```bash
# 1. جهّز البيئة مع WEBHOOK_URL
cp .env.example .env
nano .env
# أضف: WEBHOOK_URL=https://bot.example.com

# 2. عدّل nginx.conf (استبدل example.com بنطاقك)
nano nginx/nginx.conf

# 3. شغّل nginx أولاً للتحقق من النطاق
docker compose --profile webhook up -d nginx

# 4. استخرج شهادة SSL
docker compose --profile webhook run --rm certbot

# 5. شغّل البوت
docker compose --profile webhook up -d bot

# 6. تحقق من السجلات
docker compose --profile webhook logs -f bot
```

---

### أوامر مفيدة

```bash
# ── Polling ────────────────────────────────────────
docker compose logs -f bot          # سجلات مباشرة
docker compose down                  # إيقاف
docker compose up -d --build         # إعادة بناء بعد تعديل الكود

# ── Webhook ────────────────────────────────────────
docker compose --profile webhook logs -f
docker compose --profile webhook down
docker compose --profile webhook up -d --build

# ── تجديد شهادة SSL (كل 90 يوماً) ─────────────────
docker compose --profile webhook run --rm certbot renew
docker compose --profile webhook restart nginx

# ── دخول الحاوية للفحص ──────────────────────────────
docker compose exec bot bash
```

### ملاحظات عن البيانات

- مجلد `./bot_data/` على السيرفر يحفظ بيانات المستخدمين خارج الحاوية
- ملفات `config.json` و `channels.json` و `packages.json` مُربوطة مباشرةً
- لن تفقد أي بيانات عند إعادة بناء أو تحديث الصورة

---

## 🛡️ الأمان

- **لا ترفع** ملف `.env` على GitHub أبداً
- يُنصح بإنشاء مستودع **Private**
- بيانات المستخدمين مخزنة في ملفات JSON — للإنتاج الضخم استخدم PostgreSQL
- ملفات `users.json` و `analytics.json` مُضافة في `.gitignore` و `.dockerignore`

---

## 🐛 المشاكل الشائعة

| المشكلة | الحل |
|---------|------|
| `BOT_TOKEN غير موجود` | تأكد من وجود `.env` مع القيمة الصحيحة |
| `curl_cffi ImportError` | تأكد من الإصدار: `pip install curl-cffi==0.10.0` |
| TikTok لا يعمل | IP عنوان الخادم محجوب — انتقل لـ VPS بـ IP سكني |
| الملف كبير جداً | عدّل `max_file_size_mb` في `config.json` |
| البوت لا يرد | تحقق من `BOT_TOKEN` وأن البوت غير مُوقف |
| Docker: permission denied | شغّل `sudo docker compose up -d` |
| Docker: port already in use | البوت لا يستخدم بورتات — الخطأ من خدمة أخرى |

---

## 📄 الرخصة

هذا المشروع للاستخدام الشخصي والتعليمي.

---

> بُني بـ ❤️ باستخدام [python-telegram-bot](https://python-telegram-bot.org/) و [yt-dlp](https://github.com/yt-dlp/yt-dlp)
