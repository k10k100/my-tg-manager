"""
البوت الرئيسي — نقطة الدخول
يُسجّل جميع المعالجات ويبدأ البولينج.

المتطلبات: BOT_TOKEN و ADMIN_ID في متغيرات البيئة (أو ملف .env)
"""
import os
import logging

# ─── تحميل متغيرات البيئة من ملف .env إذا وُجد (للتشغيل المحلي) ─────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv غير مثبتة — لا مشكلة على السيرفر

# ─── تهيئة قاعدة البيانات (إذا كان DATABASE_URL مضبوطاً) ────────────────────
# يعمل هذا الكود دائماً — إذا لم يكن DATABASE_URL موجوداً يتجاهله بهدوء
from modules.db import init_pool
init_pool()

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    filters,
    ContextTypes
)

# ─── استيراد جميع الوحدات ────────────────────────────────────────────────────
from modules.users import register_user, get_user, update_last_active, is_idle_user
from modules.subscription import require_subscription, check_and_update_channel_goals
from modules.downloader import (
    handle_download_request, is_supported_url,
    get_enabled_platforms_text, handle_instagram_callback
)
from modules.referrals import handle_referral_info
from modules.store import handle_store, handle_buy_callback
from modules.ads import handle_ad_submission, handle_ad_callback
from modules.admin import (
    handle_admin_panel, handle_stats, handle_add_points,
    handle_broadcast, handle_admin_callback, handle_admin_conversation,
    is_admin, ADMIN_ID, load_config, save_config,
    handle_set_start_message, handle_set_rights_message,
    handle_add_quote, handle_delete_quote, handle_list_quotes,
)
from modules.payments import (
    handle_buy_stars, handle_stars_callback,
    handle_pre_checkout, handle_successful_payment
)
from modules.messages import get_start_message
from modules.scheduler import scheduler_loop
from modules.backup import auto_backup_loop
from modules.alerts import alerts_loop

# ─── إعداد السجل ─────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── توكن البوت من متغيرات البيئة ────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")


# ─── بناء لوحة المفاتيح الرئيسية ────────────────────────────────────────────
def build_menu(user_id):
    """
    يُنشئ لوحة مفاتيح ديناميكية من buttons.json.
    الأدمن يمكنه تغيير الأسماء والترتيب من لوحة التحكم.
    يُضيف زر الأدمن للمسؤولين فقط.
    """
    from modules.buttons_config import build_visible_layout
    visible = build_visible_layout()  # صفوف الأزرار المرئية فقط
    base = [
        [KeyboardButton(btn["label"]) for btn in row]
        for row in visible
    ]
    if is_admin(user_id):
        base.append([KeyboardButton("⚙️ الأدمن")])
    return ReplyKeyboardMarkup(base, resize_keyboard=True)


# ─── /start ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    يُعالج أمر /start — يُسجّل المستخدم الجديد ويتحقق من رابط الإحالة.
    """
    from modules.analytics import track_activity, track_button
    user = update.effective_user
    args = context.args
    # استخراج معرّف المُحيل من رابط /start إن وُجد
    referred_by = int(args[0]) if args and args[0].isdigit() else None

    was_idle = is_idle_user(user.id)
    is_new, _ = register_user(user.id, user.username, user.first_name, referred_by)
    update_last_active(user.id)
    track_activity(user.id)
    track_button("start")
    menu = build_menu(user.id)

    if is_new:
        # رسالة الترحيب للمستخدم الجديد من الإعدادات
        custom_msg = get_start_message(user.first_name)
        if custom_msg:
            platforms_txt = get_enabled_platforms_text()
            custom_msg = custom_msg.replace("{platforms}", platforms_txt)
            welcome = custom_msg
        else:
            welcome = (
                f"👋 مرحباً *{user.first_name}*!\n\n"
                "🤖 أنا بوت تحميل متكامل من 9 منصات.\n\n"
                "🎁 أحِل أصدقاءك واربح نقاطاً\n"
                "🛒 أنفق نقاطك في المتجر\n\n"
                "اختر من القائمة أدناه:"
            )
        await update.message.reply_text(welcome, reply_markup=menu, parse_mode="Markdown")
    elif was_idle:
        # رسالة ترحيب بالعودة للمستخدم الغائب
        await update.message.reply_text(
            f"👋 مرحباً بعودتك *{user.first_name}*! نورت البوت.",
            reply_markup=menu, parse_mode="Markdown"
        )
    else:
        # مستخدم موجود يُعيد /start — أرسل القائمة فقط
        await update.message.reply_text(
            f"أهلاً *{user.first_name}* 👋\nاختر من القائمة:",
            reply_markup=menu, parse_mode="Markdown"
        )


# ─── /help ───────────────────────────────────────────────────────────────────
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يعرض رسالة المساعدة"""
    platforms = get_enabled_platforms_text()
    await update.message.reply_text(
        "📌 *كيفية الاستخدام:*\n\n"
        "1️⃣ أرسل رابط الفيديو مباشرةً\n"
        "2️⃣ انتظر قليلاً حتى يُرسل البوت الملف\n\n"
        f"*المنصات المدعومة:*\n{platforms}\n\n"
        "💡 للدعم: تواصل مع الأدمن عبر زر دعم",
        parse_mode="Markdown"
    )


# ─── معالج الرسائل النصية (لوحة المفاتيح + الروابط) ─────────────────────────
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    يُوجّه كل رسالة نصية للمعالج المناسب:
    - أزرار القائمة → الوظيفة المقابلة
    - روابط → download
    - حالة محادثة الأدمن → handle_admin_conversation
    """
    from modules.analytics import track_activity, track_button

    text = update.message.text.strip() if update.message.text else ""
    user_id = update.effective_user.id
    update_last_active(user_id)
    track_activity(user_id)

    # ── التحقق من حالة محادثة الأدمن (إدخال بيانات لوحة التحكم) ────────────
    admin_state = context.user_data.get("admin_state")
    if admin_state:
        await handle_admin_conversation(update, context)
        return

    # ── أزرار القائمة الرئيسية (التوجيه بالمفتاح لا بالنص) ──────────────────
    # يبحث عن المفتاح المرتبط بالتسمية الحالية — يعمل حتى بعد تغيير الاسم
    from modules.buttons_config import get_label_to_key
    label_to_key = get_label_to_key()
    btn_key = label_to_key.get(text, "")

    if btn_key == "download":
        track_button("download")
        await update.message.reply_text(
            "📎 أرسل رابط الفيديو مباشرةً وسأحمّله لك!\n\n"
            f"المنصات المدعومة:\n{get_enabled_platforms_text()}"
        )

    elif btn_key == "store":
        track_button("store")
        await handle_store(update, context)

    elif btn_key == "referral":
        track_button("referrals")
        await handle_referral_info(update, context)

    elif btn_key == "ad":
        track_button("ad")
        await handle_ad_submission(update, context)

    elif btn_key == "support":
        track_button("support")
        config = load_config()
        support = config.get("support_username", "")
        msg = f"📞 للتواصل مع الدعم: @{support}" if support else "📞 تواصل مع الأدمن مباشرةً."
        await update.message.reply_text(msg)

    elif btn_key == "vip":
        track_button("vip")
        config = load_config()
        cost = config.get("vip_cost_points", 500)
        user = get_user(user_id)
        vip  = user.get("is_vip", False) if user else False
        if vip:
            await update.message.reply_text("✅ أنت بالفعل عضو VIP!")
        else:
            await update.message.reply_text(
                f"👑 *مميزات VIP:*\n\n"
                "✅ تحميل بلا حدود يومية\n"
                "⚡ أولوية في الطابور\n"
                "🚫 بدون إعلانات\n\n"
                f"💰 التكلفة: {cost} نقطة\n\n"
                "اذهب إلى 🛒 المتجر للشراء.",
                parse_mode="Markdown"
            )

    elif btn_key == "buy_stars":
        track_button("buy_stars")
        await handle_buy_stars(update, context)

    elif btn_key == "my_account":
        track_button("my_account")
        user = get_user(user_id)
        if not user:
            await update.message.reply_text("❌ ابدأ البوت بـ /start أولاً")
            return
        vip_txt = "👑 VIP" if user.get("is_vip") else "عادي"
        config  = load_config()
        limit   = config.get("download_limit_free", 5)
        used    = user.get("downloads_today", 0)
        await update.message.reply_text(
            f"📊 *حسابي*\n\n"
            f"👤 الاسم: {user.get('first_name','')}\n"
            f"🆔 المعرّف: `{user_id}`\n"
            f"💰 النقاط: *{user.get('points', 0)}*\n"
            f"🏅 الحساب: *{vip_txt}*\n"
            f"👥 الإحالات: *{user.get('referrals', 0)}*\n"
            f"📥 تحميلات اليوم: *{used}/{limit}*",
            parse_mode="Markdown"
        )

    elif btn_key == "refresh":
        track_button("refresh")
        await check_and_update_channel_goals(context.bot)
        menu = build_menu(user_id)
        await update.message.reply_text("✅ تم التحديث.", reply_markup=menu)

    elif text == "⚙️ الأدمن":
        # زر الأدمن ثابت — لا يُغيَّر اسمه
        track_button("admin")
        if is_admin(user_id):
            await handle_admin_panel(update, context)
        else:
            await update.message.reply_text("⛔ غير مصرح لك بذلك.")

    elif is_supported_url(text):
        await handle_download_request(update, context)

    else:
        await update.message.reply_text(
            "💡 أرسل رابط فيديو للتحميل، أو اضغط من القائمة."
        )


# ─── معالج أزرار InlineKeyboard ──────────────────────────────────────────────
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    يُوجّه نقرات الأزرار المضمّنة للمعالج الصحيح بناءً على بادئة البيانات.
    """
    query = update.callback_query
    data  = query.data or ""

    if data == "check_sub":
        # زر التحقق من الاشتراك
        from modules.subscription import check_subscriptions
        missing = await check_subscriptions(context.bot, update.effective_user.id)
        if missing:
            await query.answer("❌ لم تشترك بعد في جميع القنوات!", show_alert=True)
        else:
            await query.answer("✅ شكراً! يمكنك الآن استخدام البوت.", show_alert=True)
            await query.message.delete()

    elif data.startswith("ig_"):
        await handle_instagram_callback(update, context)

    elif data.startswith("admin"):
        await handle_admin_callback(update, context)

    elif data.startswith("buy_"):
        await handle_buy_callback(update, context)

    elif data.startswith("stars_"):
        await handle_stars_callback(update, context)

    elif data.startswith("ad_"):
        await handle_ad_callback(update, context)

    else:
        await query.answer()


# ─── إعدادات Webhook من متغيرات البيئة ──────────────────────────────────────
# اتركها فارغة لاستخدام Polling (الوضع الافتراضي)
WEBHOOK_URL    = os.environ.get("WEBHOOK_URL", "").rstrip("/")   # مثال: https://bot.example.com
WEBHOOK_PORT   = int(os.environ.get("WEBHOOK_PORT", "8443"))     # البورت الداخلي
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")           # سر اختياري لتأمين إضافي


# ─── نقطة الدخول الرئيسية ────────────────────────────────────────────────────
def main():
    import asyncio

    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN غير موجود في متغيرات البيئة!")

    app = Application.builder().token(BOT_TOKEN).build()

    # ── تسجيل المعالجات ──────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  help_cmd))

    # معالجات الدفع بـ Telegram Stars
    app.add_handler(PreCheckoutQueryHandler(handle_pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, handle_successful_payment))

    # معالج الأزرار المضمّنة
    app.add_handler(CallbackQueryHandler(callback_handler))

    # معالج الرسائل النصية (الأزرار والروابط والمحادثات)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # ── مهمة ما بعد التشغيل: المُجدول + أهداف القنوات ────────────────────────
    async def post_init(application):
        from modules.users import load_users
        asyncio.create_task(scheduler_loop(application.bot, load_users))
        logger.info("⏰ حلقة الجدولة تعمل في الخلفية")
        asyncio.create_task(auto_backup_loop(application.bot, ADMIN_ID))
        logger.info("💾 حلقة النسخ الاحتياطي التلقائي تعمل في الخلفية")
        asyncio.create_task(alerts_loop(application.bot, ADMIN_ID))
        logger.info("🔔 حلقة التنبيهات التلقائية تعمل في الخلفية")

    app.post_init = post_init

    # ════════════════════════════════════════════════════════════════════
    #  اختيار وضع التشغيل: Webhook أو Polling
    #  ─────────────────────────────────────────────────────────────────
    #  Webhook: أسرع وأكفأ للإنتاج — يحتاج HTTPS ونطاق عام
    #  Polling:  الأبسط للتطوير المحلي — يعمل بدون HTTPS أو نطاق
    # ════════════════════════════════════════════════════════════════════
    if WEBHOOK_URL:
        # ── وضع Webhook ──────────────────────────────────────────────────
        # البوت يستمع على WEBHOOK_PORT ، والـ nginx يعيد التوجيه من 443
        url_path = BOT_TOKEN  # يُستخدم التوكن كمسار سري للحماية

        webhook_kwargs = dict(
            listen="0.0.0.0",
            port=WEBHOOK_PORT,
            url_path=url_path,
            webhook_url=f"{WEBHOOK_URL}/{url_path}",
            allowed_updates=Update.ALL_TYPES,
        )

        # أضف WEBHOOK_SECRET إذا كان مضبوطاً (يتحقق Telegram منه في الهيدر)
        if WEBHOOK_SECRET:
            webhook_kwargs["secret_token"] = WEBHOOK_SECRET

        logger.info(
            f"🔗 وضع Webhook نشط\n"
            f"   URL: {WEBHOOK_URL}/{url_path}\n"
            f"   البورت الداخلي: {WEBHOOK_PORT}"
        )
        app.run_webhook(**webhook_kwargs)

    else:
        # ── وضع Polling ───────────────────────────────────────────────────
        # يلغي أي Webhook سابق تلقائياً ثم يبدأ الاستطلاع
        logger.info("📡 وضع Polling نشط (لا يوجد WEBHOOK_URL)")
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,  # تجاهل الرسائل المتراكمة عند إعادة التشغيل
        )


if __name__ == "__main__":
    main()

