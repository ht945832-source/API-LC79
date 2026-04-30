import os
import time
import threading
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

app = Flask(__name__)
CORS(app)

# --- DATA STORE ---
data_store = {
    "last_session": None,
    "last_total": None,
    "history_learning": {str(i): {"tai": 0, "xiu": 0, "count": 0} for i in range(3, 19)},
    "status": "Khoi dong..."
}

def monitor_md5_game():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        data_store["status"] = f"Loi Driver: {str(e)}"
        return

    while True:
        try:
            driver.get("https://lc79b.bet/")
            wait = WebDriverWait(driver, 30)
            
            # Click MD5 Tab
            md5_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'MD5')]")))
            md5_btn.click()
            time.sleep(5) 

            # Placeholder Selectors - Update these based on HTML Inspect
            try:
                # Update these classes with real ones from game
                session_el = driver.find_element(By.CSS_SELECTOR, ".md5-session-id") 
                dice_els = driver.find_elements(By.CSS_SELECTOR, ".md5-dice-item")
                
                s_id = session_el.text.strip()
                vals = [int(d.text.strip()) for d in dice_els if d.text.strip().isdigit()]
                
                if vals:
                    total = sum(vals)
                    res = "TAI" if total >= 11 else "XIU"

                    if s_id != data_store["last_session"]:
                        if data_store["last_total"] is not None:
                            prev = str(data_store["last_total"])
                            data_store["history_learning"][prev]["count"] += 1
                            if res == "TAI":
                                data_store["history_learning"][prev]["tai"] += 1
                            else:
                                data_store["history_learning"][prev]["xiu"] += 1
                        
                        data_store["last_session"] = s_id
                        data_store["last_total"] = total
                        data_store["status"] = f"OK - Phien: {s_id}"
            except:
                data_store["status"] = "Dang quet... (Cho phien moi)"
        except Exception as e:
            data_store["status"] = f"Loi: {str(e)[:50]}"
        
        time.sleep(20)

threading.Thread(target=monitor_md5_game, daemon=True).start()

@app.route('/')
def home():
    return "API HOANGDZ ONLINE. Check /api/data or /user"

@app.route('/api/data')
def get_data():
    results = []
    for score, data in data_store["history_learning"].items():
        rate, predict = 0, "CHO"
        if data["count"] > 0:
            if data["tai"] >= data["xiu"]:
                rate = int((data["tai"] / data["count"]) * 100)
                predict = "TAI"
            else:
                rate = int((data["xiu"] / data["count"]) * 100)
                predict = "XIU"
        results.append({"score": score, "predict": predict, "rate": rate, "data_count": data["count"], "status": "MANH" if data["count"] > 5 else "HOC"})
    return jsonify({"phien": data_store["last_session"], "status": data_store["status"], "predictions": results})

@app.route('/user')
def user():
    return render_template_string('''
    <body style="background:#000;color:#0f0;font-family:monospace;">
        <div id="s">Loading...</div><div id="a"></div>
        <script>
            async function u(){
                const r=await fetch('/api/data');const d=await r.json();
                document.getElementById('s').innerText=`PH_HIEN: ${d.phien} | ${d.status}`;
                let h=''; d.predictions.forEach(p=>{
                    h+=`<div>[${p.score}] -> ${p.predict} ${p.rate}% | DATA:${p.data_count} | ${p.status}</div>`;
                });
                document.getElementById('a').innerHTML=h;
            }
            setInterval(u,5000);u();
        </script>
    </body>''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
