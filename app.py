import hashlib, time, os
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CẤU HÌNH HỆ THỐNG ---
config = {
    "admin_key": "hoangdz_vip_2026",
    "base_p": 915000,
    "cycle": 48.0, 
    "offset": 0.0,
    "start_time": time.time(),
    "analyze_duration": 5
}

def solve_api_logic(p):
    seed = f"V24-FINAL-{p}-HOANGDZ"
    h = hashlib.sha256(seed.encode()).hexdigest()
    d1 = (int(h[2:4], 16) % 6) + 1
    d2 = (int(h[12:14], 16) % 6) + 1
    d3 = (int(h[22:24], 16) % 6) + 1
    total = d1 + d2 + d3
    res = "TÀI" if total >= 11 else "XỈU"
    rate_seed = int(h[60:62], 16) % 37 
    final_rate = 50 + rate_seed
    return [d1, d2, d3], total, res, f"{final_rate}%"

# --- GIAO DIỆN ADMIN ---
ADMIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HOANGDZ - V24 ADMIN</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .box { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 25px; width: 320px; text-align: center; }
        input { width: 100%; padding: 10px; margin-top: 10px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 12px; margin-top: 15px; border-radius: 6px; border: none; font-weight: bold; cursor: pointer; }
        .btn-sync { background: #238636; color: white; }
        .btn-adj { background: #30363d; color: white; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="box">
        <h2 style="color:#58a6ff">V24 SUPER SYNC</h2>
        <input type="number" id="p" placeholder="Phiên hiện tại">
        <input type="number" id="c" value="48" step="0.1" placeholder="Chu kỳ (s)">
        <p id="off_display">Độ lệch: 0.0s</p>
        <button class="btn-adj" onclick="adj(-0.1)">- 0.1s (Nhanh hơn)</button>
        <button class="btn-adj" onclick="adj(0.1)">+ 0.1s (Chậm lại)</button>
        <button class="btn-sync" onclick="send()">ĐỒNG BỘ NGAY</button>
        <div id="stt" style="margin-top:10px; color:#7ee787">Sẵn sàng</div>
    </div>
    <script>
        let o = 0.0;
        function adj(v) { o = parseFloat((o+v).toFixed(1)); document.getElementById('off_display').innerText = "Độ lệch: " + o + "s"; send(); }
        async function send() {
            await fetch('/admin/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ p: document.getElementById('p').value, c: document.getElementById('c').value, o: o })
            });
            document.getElementById('stt').innerText = "Đã đồng bộ!";
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home(): return render_template_string(ADMIN_HTML)

@app.route('/admin/update', methods=['POST'])
def update():
    d = request.json
    if d.get("p"): config["base_p"] = int(d.get("p"))
    config["cycle"] = float(d.get("c", 48.0))
    config["offset"] = float(d.get("o", 0.0))
    config["start_time"] = time.time()
    return jsonify({"status": "ok"})

@app.route('/api/data')
def get_api():
    now = time.time()
    elapsed = (now - config["start_time"]) - config["offset"]
    p_passed = int(elapsed // config["cycle"])
    curr_p = config["base_p"] + p_passed
    cd = config["cycle"] - (elapsed % config["cycle"])
    
    if cd > (config["cycle"] - config["analyze_duration"]):
        return jsonify({"phien": curr_p, "countdown": round(cd, 1), "du_doan": "PHÂN TÍCH...", "ti_le": "...", "status": "ANALYZING"})
    
    dice, total, pred, rate = solve_api_logic(curr_p)
    return jsonify({"phien": curr_p, "countdown": round(cd, 1), "du_doan": pred, "ti_le": rate, "xuc_xac": dice, "status": "READY"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
