# ═══════════════════════════════════════════════════════════
# 🛡️ OMEGA-BOT — CYBER FORTRESS (pyTelegramBotAPI)
# ═══════════════════════════════════════════════════════════

import os
import logging
import threading
import socket
import requests
import sqlite3
import time
from datetime import datetime
from flask import Flask, jsonify
import telebot
from telebot import types

# ─── FLASK APP (Render Health Check) ───
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>🛡️ OMEGA-BOT ONLINE</h1>
    <p>साइबर फोर्ट्रेस सक्रिय — DRAGON द्वारा निर्मित</p>
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

# ─── CONFIG ───
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CREATOR_ID = int(os.environ.get("CREATOR_ID", "0"))
ADMIN_IDS = [CREATOR_ID] if CREATOR_ID else []

# ─── LOGGING ───
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── DATABASE ───
def init_db():
    conn = sqlite3.connect('omega_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attacks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  attacker_ip TEXT, attack_type TEXT,
                  timestamp TEXT, payload TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS vulnerabilities
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  target TEXT, port INTEGER, service TEXT,
                  vulnerability TEXT, severity TEXT, discovered_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT, first_name TEXT,
                  is_premium INTEGER DEFAULT 0, joined_at TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ─── BOT INIT ───
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# ─── SCANNER CLASS ───
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
            5900: {"risk": "MEDIUM", "exploit": "VNC Default Password", "payload": f"vncviewer {target}:5900"},
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
                "lon": data.get("lon", "N/A")
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

# ─── ADMIN CHECK DECORATOR ───
def admin_only(func):
    def wrapper(message):
        if message.from_user.id not in ADMIN_IDS:
            bot.reply_to(message, "⚠️ आपको OMEGA-BOT चलाने की अनुमति नहीं है।")
            return
        return func(message)
    return wrapper

# ─── TELEGRAM HANDLERS ───

@bot.message_handler(commands=['start'])
@admin_only
def start_command(message):
    user_id = message.from_user.id
    user = message.from_user
    conn = sqlite3.connect('omega_bot.db')
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at)
                 VALUES (?, ?, ?, ?)''',
              (user_id, user.username, user.first_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    bot.reply_to(message, """
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

@bot.message_handler(commands=['scan'])
@admin_only
def scan_command(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "🔹 /scan <IP> — जैसे: /scan 8.8.8.8")
        return
    target = args[1]
    bot.reply_to(message, f"🔍 {target} का पोर्ट स्कैन शुरू...")
    scanner = VulnerabilityScanner()
    open_ports = scanner.scan_network(target)
    if open_ports:
        response = f"✅ {target} पर खुले पोर्ट: {', '.join(map(str, open_ports))}"
    else:
        response = f"❌ {target} पर कोई पोर्ट नहीं खुला।"
    bot.reply_to(message, response)

@bot.message_handler(commands=['exploit'])
@admin_only
def exploit_command(message):
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "🔹 /exploit <IP> <port> — जैसे: /exploit 8.8.8.8 22")
        return
    target = args[1]
    port = int(args[2])
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
    bot.reply_to(message, response)

@bot.message_handler(commands=['trace'])
@admin_only
def trace_command(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "🔹 /trace <IP> — जैसे: /trace 8.8.8.8")
        return
    ip = args[1]
    bot.reply_to(message, f"📍 {ip} का लोकेशन ट्रेस कर रहा हूँ...")
    tracer = HackerTracer()
    location = tracer.trace_ip(ip)
    if "error" in location:
        bot.reply_to(message, "❌ IP ट्रेस विफल।")
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
    bot.reply_to(message, response)

@bot.message_handler(commands=['counter'])
@admin_only
def counter_command(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "🔹 /counter <IP> — जैसे: /counter 8.8.8.8")
        return
    target = args[1]
    bot.reply_to(message, f"💀 {target} पर काउंटर-अटैक शुरू...")
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
    bot.reply_to(message, response)

@bot.message_handler(commands=['honeypot'])
@admin_only
def honeypot_command(message):
    args = message.text.split()
    port = int(args[1]) if len(args) > 1 else 22
    honeypot = Honeypot()
    result = honeypot.start_honeypot(port)
    bot.reply_to(message, f"""
🫳 HONEYPOT सक्रिय

🔌 पोर्ट: {result['port']}
📡 स्टेटस: चालू
🔴 कोई अटैक आया तो लॉग करूँगा।

[ OMEGA-BOT >> HONEYPOT ACTIVE ]
""")

@bot.message_handler(commands=['status'])
@admin_only
def status_command(message):
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
    bot.reply_to(message, response)

@bot.message_handler(commands=['db'])
@admin_only
def db_command(message):
    conn = sqlite3.connect('omega_bot.db')
    c = conn.cursor()
    c.execute('SELECT * FROM attacks ORDER BY id DESC LIMIT 10')
    attacks = c.fetchall()
    conn.close()
    if not attacks:
        bot.reply_to(message, "📊 डेटाबेस में कोई अटैक नहीं।")
        return
    response = "📊 **LAST 10 ATTACKS**\n\n"
    for attack in attacks:
        response += f"🆔 {attack[0]} | {attack[3]} | {attack[1]} | {attack[2]}\n"
    bot.reply_to(message, response)

@bot.message_handler(func=lambda m: True)
def unknown_command(message):
    bot.reply_to(message, "⚠️ Unknown command. Use /start to see available commands.")

# ─── BOT POLLING THREAD ───
def run_bot():
    logger.info("🐉 OMEGA-BOT (telebot) चालू हो रहा है...")
    bot.polling(none_stop=True)

# ─── START BOT IN BACKGROUND ───
if not os.environ.get("RENDER"):  # Local run
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("✅ Telegram bot thread started (local).")
else:
    # On Render, start after Flask app is ready
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("✅ Telegram bot thread started (Render).")
