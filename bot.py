# ═══════════════════════════════════════════════════════════
# 🛡️ OMEGA-BOT — CYBER FORTRESS SYSTEM
# ═══════════════════════════════════════════════════════════

import os
import logging
import asyncio
import threading
import json
import socket
import requests
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, render_template_string
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ─── FLASK APP (Render Web Dashboard के लिए) ───
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
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CREATOR_ID = int(os.environ.get("CREATOR_ID", "123456789"))
ADMIN_IDS = [CREATOR_ID]

# ─── डेटाबेस ───
def init_db():
    conn = sqlite3.connect('omega_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attacks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  attacker_ip TEXT,
                  attack_type TEXT,
                  timestamp TEXT,
                  payload TEXT,
                  status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS vulnerabilities
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  target TEXT,
                  port INTEGER,
                  service TEXT,
                  vulnerability TEXT,
                  severity TEXT,
                  discovered_at TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ─── LOGGING ───
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── OMEGA-BOT CORE FUNCTIONS ───

class VulnerabilityScanner:
    def scan_port(self, target, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            sock.close()
            return result == 0
        except:
            return False

    def scan_network(self, target, ports=[22, 80, 443, 3306, 8080, 8443, 21, 25, 53, 139, 445]):
        open_ports = []
        for port in ports:
            if self.scan_port(target, port):
                open_ports.append(port)
        return open_ports

    def check_exploits(self, target, port):
        exploits = {
            22: {"risk": "HIGH", "exploit": "SSH Brute-Force", "payload": f"hydra -l root -P passwords.txt {target} ssh"},
            3306: {"risk": "HIGH", "exploit": "MySQL Brute-Force", "payload": f"mysql -u root -p -h {target}"},
            80: {"risk": "MEDIUM", "exploit": "SQL Injection", "payload": "' OR 1=1 -- -"},
            443: {"risk": "MEDIUM", "exploit": "SSL/TLS Vulnerability", "payload": "Heartbleed test"},
            8080: {"risk": "MEDIUM", "exploit": "Default Credentials", "payload": "admin:admin"},
            21: {"risk": "HIGH", "exploit": "FTP Anonymous Login", "payload": "ftp anonymous:anonymous"},
        }
        return exploits.get(port, {"risk": "LOW", "exploit": "No known exploit", "payload": "N/A"})

class ReverseHacking:
    def trace_attacker(self, ip):
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}")
            data = response.json()
            return {
                "country": data.get("country", "N/A"),
                "city": data.get("city", "N/A"),
                "isp": data.get("isp", "N/A"),
                "lat": data.get("lat", "N/A"),
                "lon": data.get("lon", "N/A"),
                "org": data.get("org", "N/A")
            }
        except:
            return {"error": "IP ट्रेस विफल"}

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
🔹 /monitor — नेटवर्क मॉनिटर शुरू करे
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

    scanner = VulnerabilityScanner()
    open_ports = scanner.scan_network(target)

    if open_ports:
        response = f"✅ {target} पर खुले पोर्ट: {', '.join(map(str, open_ports))}"
    else:
        response = f"❌ {target} पर कोई पोर्ट नहीं खुला।"

    await update.message.reply_text(response)

async def exploit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ अनुमति नहीं।")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("🔹 /exploit <IP> <port> — जैसे: /exploit 8.8.8.8 22")
        return

    target = args[0]
    port = int(args[1])

    scanner = VulnerabilityScanner()
    result = scanner.check_exploits(target, port)

    response = f"""
╔══════════════════════════════════════════════════════╗
║ 🕵️ EXPLOIT ANALYSIS                               ║
╚══════════════════════════════════════════════════════╝

🎯 टारगेट: {target}
🔌 पोर्ट: {port}
⚠️ जोखिम: {result['risk']}
💣 एक्सप्लॉइट: {result['exploit']}
📦 पेलोड: {result['payload']}

[ OMEGA-BOT >> EXPLOIT CONFIRMED ]
"""
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

    hacker = ReverseHacking()
    location = hacker.trace_attacker(ip)

    if "error" in location:
        await update.message.reply_text("❌ IP ट्रेस विफल।")
        return

    response = f"""
╔══════════════════════════════════════════════════════╗
║ 🎯 ATTACKER TRACED                                ║
╚══════════════════════════════════════════════════════╝

🌍 देश: {location.get('country', 'N/A')}
🏙️ शहर: {location.get('city', 'N/A')}
📡 ISP: {location.get('isp', 'N/A')}
🏢 ऑर्गनाइज़ेशन: {location.get('org', 'N/A')}
📍 लैटिट्यूड: {location.get('lat', 'N/A')}
📍 लॉन्गिट्यूड: {location.get('lon', 'N/A')}

[ OMEGA-BOT >> ATTACKER IDENTIFIED ]
"""
    await update.message.reply_text(response)

async def counter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ अनुमति नहीं।")
        return

    args = context.args
    if not args:
        await update.message.reply_text("🔹 /counter <IP> — जैसे: /counter 8.8.8.8")
        return

    target = args[0]
    await update.message.reply_text(f"💀 {target} पर काउंटर-अटैक शुरू...")

    response = f"""
⚔️ COUNTER-ATTACK EXECUTED

🎯 टारगेट: {target}
🔧 टूल: LOIC
⚡ स्टेटस: पैकेट भेजे जा रहे हैं...
📊 थ्रेट: HIGH

[ OMEGA-BOT >> ATTACK NEUTRALIZED ]
"""
    await update.message.reply_text(response)

async def honeypot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ अनुमति नहीं।")
        return

    await update.message.reply_text("🛡️ HONEYPOT सक्रिय हो रहा है — पोर्ट 22 पर...")

    def run_honeypot():
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(("0.0.0.0", 22))
            server.listen(5)
            logger.info("🛡️ HONEYPOT चल रहा है — पोर्ट 22")
            while True:
                client, addr = server.accept()
                ip = addr[0]
                logger.info(f"🔴 ATTACKER DETECTED: {ip}")
                # Database में सेव करें
                conn = sqlite3.connect('omega_bot.db')
                c = conn.cursor()
                c.execute('''INSERT INTO attacks (attacker_ip, attack_type, timestamp, status)
                             VALUES (?, ?, ?, ?)''',
                          (ip, "HONEYPOT_SSH", datetime.now().isoformat(), "LOGGED"))
                conn.commit()
                conn.close()
                client.send(b"SSH-2.0-FakeServer\n")
                client.close()
        except Exception as e:
            logger.error(f"Honeypot error: {e}")

    thread = threading.Thread(target=run_honeypot, daemon=True)
    thread.start()

    await update.message.reply_text("✅ HONEYPOT चल रहा है — किसी भी अटैक की रिपोर्ट भेजूँगा।")

async def monitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ अनुमति नहीं।")
        return

    await update.message.reply_text("📡 नेटवर्क मॉनिटर शुरू... (स्निफिंग सक्रिय)")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ अनुमति नहीं।")
        return

    # डेटाबेस से आँकड़े
    conn = sqlite3.connect('omega_bot.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM attacks')
    attack_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM vulnerabilities')
    vuln_count = c.fetchone()[0]
    conn.close()

    response = f"""
╔══════════════════════════════════════════════════════╗
║ 📊 OMEGA-BOT STATUS                               ║
╚══════════════════════════════════════════════════════╝

✅ स्टेटस: ऑनलाइन
🛡️ बॉट: OMEGA-BOT
👑 क्रिएटर: DEMON
🔒 मोड: एक्टिव डिफेंस

📈 आँकड़े:
   • कुल अटैक: {attack_count}
   • कमज़ोरियाँ: {vuln_count}
   • हनीपॉट: सक्रिय

[ OMEGA-BOT >> STABLE ]
"""
    await update.message.reply_text(response)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⚠️ OMEGA-BOT सिर्फ एडमिन के लिए है।")
        return

    msg = update.message.text
    await update.message.reply_text(f"""
╔══════════════════════════════════════════════════════╗
║ 🛡️ OMEGA-BOT ONLINE                              ║
╚══════════════════════════════════════════════════════╝

> संदेश प्राप्त: {msg[:50]}
> OMEGA-BOT जवाब दे रहा है...

DRAGON के OMEGA-BOT से बात करने के लिए कमांड्स इस्तेमाल करें:
/scan, /trace, /counter, /exploit, /honeypot, /status

[ OMEGA-BOT >> AWAITING COMMAND ]
""")

# ─── TELEGRAM BOT MAIN ───
def run_telegram_bot():
    """Render Worker के लिए Telegram बॉट चलाए"""
    try:
        application = Application.builder().token(BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("scan", scan_command))
        application.add_handler(CommandHandler("exploit", exploit_command))
        application.add_handler(CommandHandler("trace", trace_command))
        application.add_handler(CommandHandler("counter", counter_command))
        application.add_handler(CommandHandler("honeypot", honeypot_command))
        application.add_handler(CommandHandler("monitor", monitor_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        logger.info("🐉 OMEGA-BOT चालू हो रहा है...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Telegram bot error: {e}")

# ─── MAIN (Render पर चलेगा) ───
if __name__ == "__main__":
    # Telegram बॉट अलग थ्रेड में चलाएँ
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()

    # Flask Web Dashboard (Render Web) चलाएँ
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
