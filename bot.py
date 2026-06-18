# ═══════════════════════════════════════════════════════════
# 🛡️ OMEGA-BOT — CYBER FORTRESS SYSTEM
# ═══════════════════════════════════════════════════════════

import os
import logging
import threading
import socket
import json
import sqlite3
import requests
from datetime import datetime
from flask import Flask, jsonify, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ─── FLASK APP ───
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🛡️ OMEGA-BOT</title>
        <style>
            body { background: #0a0a0a; color: #ff0000; font-family: 'Courier New', monospace; text-align: center; padding: 50px; }
            h1 { font-size: 60px; text-shadow: 0 0 20px #ff0000; }
            p { font-size: 20px; color: #00ff00; }
            .status { border: 2px solid #ff0000; padding: 20px; border-radius: 10px; display: inline-block; }
            .blink { animation: blink 1s infinite; }
            @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } 100% { opacity: 1; } }
        </style>
    </head>
    <body>
        <h1>🐉 OMEGA-BOT</h1>
        <h2>🛡️ CYBER FORTRESS</h2>
        <div class="status">
            <p>✅ STATUS: <span class="blink">ONLINE</span></p>
            <p>👑 CREATOR: DEMON</p>
            <p>🔒 MODE: ACTIVE DEFENSE</p>
        </div>
        <p>⚡ "Hackers are NOT safe anymore"</p>
    </body>
    </html>
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

# ─── CONFIGURATION ───
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CREATOR_ID = int(os.environ.get("CREATOR_ID", "0"))
ADMIN_IDS = [CREATOR_ID] if CREATOR_ID else []

if not BOT_TOKEN:
    logging.error("❌ BOT_TOKEN not set!")

if not CREATOR_ID:
    logging.error("❌ CREATOR_ID not set!")

# ─── DATABASE ───
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
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  is_premium INTEGER DEFAULT 0,
                  joined_at TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ─── LOGGING ───
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── MODULES ───

class VulnerabilityScanner:
    def scan_port(self, target, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.5)
            result = sock.connect_ex((target, port))
            sock.close()
            return result == 0
        except:
            return False

    def scan_network(self, target, ports=[22, 21, 25, 53, 80, 139, 443, 445, 3306, 5432, 5900, 8080, 8443]):
        open_ports = []
        for port in ports:
            if self.scan_port(target, port):
                open_ports.append(port)
                logger.info(f"🔓 {target}:{port} OPEN")
        return open_ports

    def check_exploits(self, target, port):
        exploits = {
            22: {"risk": "HIGH", "exploit": "SSH Brute-Force", "payload": f"hydra -l root -P passwords.txt {target} ssh"},
            21: {"risk": "HIGH", "exploit": "FTP Anonymous Login", "payload": f"ftp {target} -A"},
            3306: {"risk": "HIGH", "exploit": "MySQL Default Credentials", "payload": f"mysql -u root -p -h {target}"},
            80: {"risk": "MEDIUM", "exploit": "SQL Injection", "payload": f"http://{target}/?id=1' OR '1'='1"},
            443: {"risk": "MEDIUM", "exploit": "SSL/TLS Vulnerability", "payload": f"openssl s_client -connect {target}:443"},
            8080: {"risk": "MEDIUM", "exploit": "Default Credentials", "payload": "admin:admin"},
            5432: {"risk": "HIGH", "exploit": "PostgreSQL Brute-Force", "payload": f"psql -h {target} -U postgres"},
            5900: {"risk": "MEDIUM", "exploit": "VNC Default Password", "payload": "vncviewer {target}:5900"},
        }
        return exploits.get(port, {"risk": "LOW", "exploit": "No known exploit", "payload": "N/A"})

class HackerTracer:
    def trace_ip(self, ip):
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            data = response.json()
            return {
                "country": data.get("country", "N/A"),
                "city": data.get("city", "N/A"),
                "isp": data.get("isp", "N/A"),
                "org": data.get("org", "N/A"),
                "lat": data.get("lat", "N/A"),
                "lon": data.get("lon", "N/A"),
                "timezone": data.get("timezone", "N/A")
            }
        except:
            return {"error": "IP trace failed"}

class CounterAttack:
    def ddos_counter(self, target):
        return {
            "status": "COUNTER-ATTACK READY",
            "target": target,
            "method": "SYN Flood",
            "payload": f"hping3 -S -p 80 -i u100 --flood {target}"
        }

class Honeypot:
    def start_honeypot(self, port=22):
        def run():
            try:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.bind(("0.0.0.0", port))
                server.listen(5)
                logger.info(f"🫳 HONEYPOT started on port {port}")
                while True:
                    client, addr = server.accept()
                    ip = addr[0]
                    logger.info(f"🔴 ATTACKER DETECTED: {ip}")
                    conn = sqlite3.connect('omega_bot.db')
                    c = conn.cursor()
                    c.execute('''INSERT INTO attacks (attacker_ip, attack_type, timestamp, status)
                                 VALUES (?, ?, ?, ?)''',
                              (ip, f"HONEYPOT_PORT_{port}", datetime.now().isoformat(), "LOGGED"))
                    conn.commit()
                    conn.close()
                    client.send(b"SSH-2.0-FakeServer\n")
                    client.close()
            except Exception as e:
                logger.error(f"Honeypot error: {e}")
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return {"status": "HONEYPOT STARTED", "port": port}

# ─── TELEGRAM COMMANDS ───

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = update.effective_user

    # Save user to database
    conn = sqlite3.connect('omega_bot.db')
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at)
                 VALUES (?, ?, ?, ?)''',
              (user_id, user.username, user.first_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

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
🔹 /honeypot <port> — फेक सर्वर चलाए (default: 22)
🔹 /status — बॉट की स्थिति बताए
🔹 /db — डेटाबेस स्टेटस दिखाए

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

    tracer = HackerTracer()
    location = tracer.trace_ip(ip)

    if "error" in location:
        await update.message.reply_text("❌ IP ट्रेस विफल।")
        return

    response = f"""
╔══════════════════════════════════════════════════════╗
║ 🎯 ATTACKER TRACED                                ║
╚══════════════════════════════════════════════════════╝

🌍 देश: {location.get('country')}
🏙️ शहर: {location.get('city')}
📡 ISP: {location.get('isp')}
🏢 ऑर्गनाइज़ेशन: {location.get('org')}
📍 लैटिट्यूड: {location.get('lat')}
📍 लॉन्गिट्यूड: {location.get('lon')}

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

    counter = CounterAttack()
    result = counter.ddos_counter(target)

    response = f"""
⚔️ COUNTER-ATTACK EXECUTED

🎯 टारगेट: {result['target']}
🔧 मेथड: {result['method']}
⚡ स्टेटस: पैकेट भेजे जा रहे हैं...
📊 थ्रेट: HIGH
📦 पेलोड: {result['payload']}

[ OMEGA-BOT >> ATTACK NEUTRALIZED ]
"""
    await update.message.reply_text(response)

async def honeypot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ अनुमति नहीं।")
        return

    args = context.args
    port = int(args[0]) if args else 22

    honeypot = Honeypot()
    result = honeypot.start_honeypot(port)

    await update.message.reply_text(f"""
🫳 HONEYPOT सक्रिय

🔌 पोर्ट: {result['port']}
📡 स्टेटस: चालू
🔴 कोई अटैक आया तो लॉग करूँगा।

[ OMEGA-BOT >> HONEYPOT ACTIVE ]
""")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ अनुमति नहीं।")
        return

    conn = sqlite3.connect('omega_bot.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM attacks')
    attack_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM vulnerabilities')
    vuln_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM users')
    user_count = c.fetchone()[0]
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
   • कुल यूज़र: {user_count}
   • हनीपॉट: सक्रिय

[ OMEGA-BOT >> STABLE ]
"""
    await update.message.reply_text(response)

async def db_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ अनुमति नहीं।")
        return

    conn = sqlite3.connect('omega_bot.db')
    c = conn.cursor()
    c.execute('SELECT * FROM attacks ORDER BY id DESC LIMIT 10')
    attacks = c.fetchall()
    conn.close()

    if not attacks:
        await update.message.reply_text("📊 डेटाबेस में कोई अटैक नहीं।")
        return

    response = "📊 **LAST 10 ATTACKS**\n\n"
    for attack in attacks:
        response += f"🆔 {attack[0]} | {attack[3]} | {attack[1]} | {attack[2]}\n"

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
        application.add_handler(CommandHandler("exploit", exploit_command))
        application.add_handler(CommandHandler("trace", trace_command))
        application.add_handler(CommandHandler("counter", counter_command))
        application.add_handler(CommandHandler("honeypot", honeypot_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("db", db_command))
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
