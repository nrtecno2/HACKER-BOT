# ═══════════════════════════════════════════════════════════
# 🛡️ OMEGA-BOT — CYBER FORTRESS (RENDER FIXED)
# ═══════════════════════════════════════════════════════════

import os
import logging
import threading
import socket
import requests
from datetime import datetime
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ─── FLASK APP ───
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>🛡️ OMEGA-BOT ONLINE</h1>
    <p>साइबर फोर्ट्रेस सक्रिय है — DRAGON द्वारा निर्मित</p>
    <p>📊 स्टेटस: <strong>चालू</strong></p>
    <p>🔒 सुरक्षा: <strong>सक्रिय</strong></p>
    """

@app.route('/status')
def status():
    return jsonify({
        "status": "online",
        "bot": "OMEGA-BOT",
        "creator": "DEMON",
        "mode": "ACTIVE DEFENSE",
        "timestamp": datetime.now().isoformat()
    })

# ─── कॉन्फ़िगरेशन ───
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CREATOR_ID = int(os.environ.get("CREATOR_ID", "0"))
ADMIN_IDS = [CREATOR_ID] if CREATOR_ID else []

# ─── LOGGING ───
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── TELEGRAM COMMANDS ───

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⚠️ आपको OMEGA-BOT चलाने की अनुमति नहीं है।")
        return

    await update.message.reply_text("""
╔══════════════════════════════════════════════════════╗
║ 🛡️ OMEGA-BOT — CYBER FORTRESS ACTIVE             ║
╚══════════════════════════════════════════════════════╝

> DRAGON द्वारा निर्मित
> DEMON का साइबर किला

──────────────────────────────────────────────────────────

🔹 /scan <IP> — पोर्ट स्कैन करे
🔹 /exploit <IP> <port> — एक्सप्लॉइट चेक करे
🔹 /trace <IP> — हैकर का लोकेशन ट्रेस करे
🔹 /counter <IP> — काउंटर-अटैक शुरू करे
🔹 /honeypot — फेक सर्वर चलाए
🔹 /status — बॉट की स्थिति बताए

🐉 OMEGA-BOT तैयार है — आज्ञा दें
""")

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ अनुमति नहीं।")
        return

    args = context.args
    if not args:
        await update.message.reply_text("🔹 /scan <IP> — जैसे: /scan 8.8.8.8")
        return

    target = args[0]
    await update.message.reply_text(f"🔍 {target} का पोर्ट स्कैन शुरू...")

    open_ports = []
    ports = [22, 80, 443, 3306, 8080, 8443, 21, 25, 53, 139, 445]
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            sock.close()
            if result == 0:
                open_ports.append(port)
        except:
            pass

    if open_ports:
        response = f"✅ {target} पर खुले पोर्ट: {', '.join(map(str, open_ports))}"
    else:
        response = f"❌ {target} पर कोई पोर्ट नहीं खुला।"

    await update.message.reply_text(response)

async def trace_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ अनुमति नहीं।")
        return

    args = context.args
    if not args:
        await update.message.reply_text("🔹 /trace <IP> — जैसे: /trace 8.8.8.8")
        return

    ip = args[0]
    await update.message.reply_text(f"📍 {ip} का लोकेशन ट्रेस कर रहा हूँ...")

    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        location = {
            "country": data.get("country", "N/A"),
            "city": data.get("city", "N/A"),
            "isp": data.get("isp", "N/A"),
            "org": data.get("org", "N/A")
        }
        response_msg = f"""
╔══════════════════════════════════════════════════════╗
║ 🎯 ATTACKER TRACED                                ║
╚══════════════════════════════════════════════════════╝

🌍 देश: {location.get('country')}
🏙️ शहर: {location.get('city')}
📡 ISP: {location.get('isp')}
🏢 ऑर्गनाइज़ेशन: {location.get('org')}

[ OMEGA-BOT >> ATTACKER IDENTIFIED ]
"""
    except:
        response_msg = "❌ IP ट्रेस विफल।"

    await update.message.reply_text(response_msg)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ अनुमति नहीं।")
        return

    response = """
╔══════════════════════════════════════════════════════╗
║ 📊 OMEGA-BOT STATUS                               ║
╚══════════════════════════════════════════════════════╝

✅ स्टेटस: ऑनलाइन
🛡️ बॉट: OMEGA-BOT
👑 क्रिएटर: DEMON
🔒 मोड: एक्टिव डिफेंस

[ OMEGA-BOT >> STABLE ]
"""
    await update.message.reply_text(response)

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Unknown command. Use /start to see available commands.")

# ─── TELEGRAM BOT RUNNER ───
def run_telegram_bot():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set in environment!")
        return
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("scan", scan_command))
        application.add_handler(CommandHandler("trace", trace_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_command))
        
        logger.info("🐉 OMEGA-BOT चालू हो रहा है...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"❌ Telegram bot error: {e}")

# ─── MAIN ───
if __name__ == "__main__":
    # Telegram Bot को अलग थ्रेड में चलाएँ
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # Flask Web Server चलाएँ
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 Flask server starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
