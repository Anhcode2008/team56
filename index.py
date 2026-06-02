from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import sys
import uuid
import os
import time

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = Flask(__name__)
CORS(app)

# ==================== CẤU HÌNH ====================
# ⚠️ QUAN TRỌNG: Thay URL này bằng URL thật của main.py sau khi deploy lên Replit/VPS
# Ví dụ: https://ff-bot.your-username.repl.co
BOT_SERVER_URL = os.environ.get('BOT_SERVER_URL', 'http://team56-gawc36fwm-anhcode2008s-projects.vercel.app')

# Cache lưu trạng thái request (do Vercel serverless)
request_cache = {}

# ==================== HELPER FUNCTIONS ====================

def forward_to_bot(endpoint, uid):
    """Chuyển tiếp request đến bot server chính"""
    
    # Validate UID
    if not uid:
        return None, {"status": "error", "message": "UID parameter is required"}, 400
    if not uid.isdigit():
        return None, {"status": "error", "message": "UID must contain only numbers"}, 400
    if len(uid) < 8 or len(uid) > 15:
        return None, {"status": "error", "message": "UID must be 8-15 digits long"}, 400
    
    request_id = str(uuid.uuid4())[:8]
    
    try:
        # Forward request đến main.py
        url = f"{BOT_SERVER_URL}/{endpoint}?uid={uid}"
        logging.info(f"🔄 Forwarding request {request_id} to {url}")
        
        response = requests.get(url, timeout=30)
        
        # Cache request info
        request_cache[request_id] = {
            'timestamp': time.time(),
            'endpoint': endpoint,
            'uid': uid,
            'status_code': response.status_code
        }
        
        # Lấy response từ bot
        if response.ok:
            result = response.json()
            result['gateway_request_id'] = request_id
            result['gateway_note'] = "Request forwarded to bot server"
            return result, None, response.status_code
        else:
            return None, {
                "status": "error",
                "message": f"Bot server returned error: {response.status_code}",
                "request_id": request_id
            }, response.status_code
        
    except requests.exceptions.ConnectionError:
        return None, {
            "status": "error",
            "message": f"❌ Cannot connect to bot server at {BOT_SERVER_URL}",
            "request_id": request_id,
            "solution": "1. Make sure main.py is running on Replit/VPS\n2. Check BOT_SERVER_URL environment variable\n3. Verify the URL is correct"
        }, 503
    except requests.exceptions.Timeout:
        return None, {
            "status": "error",
            "message": "⏰ Bot server timeout (30s)",
            "request_id": request_id
        }, 504
    except Exception as e:
        return None, {
            "status": "error",
            "message": f"⚠️ Error: {str(e)}",
            "request_id": request_id
        }, 500

# ==================== API ENDPOINTS ====================

@app.route('/')
def home():
    """Trang chủ API Gateway"""
    return jsonify({
        "status": "success",
        "message": "🎮 FF Squad Bot API Gateway",
        "credit": "https://t.me/anhcodeclick",
        "version": "2.0",
        "architecture": {
            "api_gateway": "Vercel (Serverless)",
            "bot_engine": "VPS/Replit (TCP Bot)",
            "communication": "HTTP API Forwarding"
        },
        "endpoints": {
            "/3": "3-player squad invite (?uid=xxx)",
            "/4": "4-player squad invite (?uid=xxx)",
            "/5": "5-player squad invite (?uid=xxx)",
            "/6": "6-player squad invite (?uid=xxx)",
            "/room": "Room spam 30x (?uid=xxx)",
            "/spm": "Squad spam 30x (?uid=xxx)",
            "/status": "Bot server status",
            "/queue": "Bot command queue",
            "/health": "Gateway health check"
        },
        "config": {
            "bot_server_url": BOT_SERVER_URL,
            "status": "⚠️ Use /health to check connection to bot server"
        }
    })

@app.route('/health')
def health_check():
    """Kiểm tra kết nối đến bot server"""
    try:
        response = requests.get(f"{BOT_SERVER_URL}/status", timeout=5)
        bot_online = response.status_code == 200
        bot_data = response.json() if bot_online else None
        status_text = "✅ Bot server is online" if bot_online else "❌ Bot server returned error"
    except Exception as e:
        bot_online = False
        bot_data = {"error": str(e)}
        status_text = f"❌ Cannot connect: {str(e)}"
    
    return jsonify({
        "status": "healthy" if bot_online else "degraded",
        "gateway": {
            "status": "online",
            "timestamp": time.time()
        },
        "bot_server": {
            "url": BOT_SERVER_URL,
            "online": bot_online,
            "status_text": status_text,
            "details": bot_data
        },
        "next_steps": [
            "If bot server is offline, deploy main.py to Replit/VPS",
            f"Set BOT_SERVER_URL environment variable to your bot URL",
            "Current BOT_SERVER_URL: " + BOT_SERVER_URL
        ]
    })

@app.route('/status')
def api_status():
    """Lấy trạng thái từ bot server"""
    result, error, status_code = forward_to_bot('status', '1')
    if error:
        return jsonify(error), status_code
    return jsonify(result)

@app.route('/queue')
def api_queue():
    """Lấy hàng đợi command từ bot server"""
    result, error, status_code = forward_to_bot('queue', '1')
    if error:
        return jsonify(error), status_code
    return jsonify(result)

@app.route('/3')
def squad_3():
    """3-player squad invite"""
    uid = request.args.get('uid', '').strip()
    result, error, status_code = forward_to_bot('3', uid)
    if error:
        return jsonify(error), status_code
    return jsonify(result)

@app.route('/4')
def squad_4():
    """4-player squad invite"""
    uid = request.args.get('uid', '').strip()
    result, error, status_code = forward_to_bot('4', uid)
    if error:
        return jsonify(error), status_code
    return jsonify(result)

@app.route('/5')
def squad_5():
    """5-player squad invite"""
    uid = request.args.get('uid', '').strip()
    result, error, status_code = forward_to_bot('5', uid)
    if error:
        return jsonify(error), status_code
    return jsonify(result)

@app.route('/6')
def squad_6():
    """6-player squad invite"""
    uid = request.args.get('uid', '').strip()
    result, error, status_code = forward_to_bot('6', uid)
    if error:
        return jsonify(error), status_code
    return jsonify(result)

@app.route('/room')
def room_spam():
    """Room spam (30 cycles)"""
    uid = request.args.get('uid', '').strip()
    result, error, status_code = forward_to_bot('room', uid)
    if error:
        return jsonify(error), status_code
    return jsonify(result)

@app.route('/spm')
def squad_spam():
    """Squad spam (30 cycles)"""
    uid = request.args.get('uid', '').strip()
    result, error, status_code = forward_to_bot('spm', uid)
    if error:
        return jsonify(error), status_code
    return jsonify(result)

@app.route('/request/<request_id>')
def check_request(request_id):
    """Kiểm tra trạng thái request (cached)"""
    if request_id in request_cache:
        return jsonify({
            "status": "success",
            "request_id": request_id,
            "data": request_cache[request_id],
            "note": "Use /queue endpoint on bot server for real-time status"
        })
    return jsonify({
        "status": "error",
        "message": "Request ID not found in gateway cache"
    }), 404

# ==================== VERCEL HANDLER ====================
handler = app

# ==================== LOCAL DEVELOPMENT ====================
if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║   🎮 FF SQUAD BOT - API GATEWAY (Development Mode)          ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Gateway running on: http://team56-gawc36fwm-anhcode2008s-projects.vercel.app              ║
║  📡 Forwarding to bot server: {}      
║  ⚠️  Make sure main.py is running on the target server!     ║
║  🔍 Test connection: http://team56-gawc36fwm-anhcode2008s-projects.vercel.app/health            ║
╚══════════════════════════════════════════════════════════════╝
    """.format(BOT_SERVER_URL))
    app.run(host='0.0.0.0', port=5000, debug=False)
