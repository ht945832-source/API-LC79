import os
import time
import threading
from flask import Flask, jsonify
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

# --- CẤU HÌNH BỘ NÃO (DATA STORE) ---
data_store = {
    "last_session": None,
    "last_total": None,
    "history_learning": {str(i): {"tai": 0, "xiu": 0, "count": 0} for i in range(3, 19)},
    "status": "Đang khởi động hệ thống..."
}

def monitor_md5_game():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # Khởi tạo driver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Lỗi khởi tạo Driver: {e}")
        return

    print("🤖 Mắt ảo đã sẵn sàng. Bắt đầu quét bàn MD5...")
    
    while True:
        try:
            driver.get("https://lc79b.bet/")
            wait = WebDriverWait(driver, 30)

            # --- NHẬN DIỆN VÀ CHỌN BÀN MD5 ---
            # Tìm bàn MD5 (Màu tím/đỏ) dựa trên text hoặc thuộc tính nhận diện
            md5_table = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'MD5')]")))
            md5_table.click()
            time.sleep(5) 

            # --- QUÉT DỮ LIỆU PHIÊN ---
            # Lưu ý: Cần cập nhật Selector chính xác khi có quyền truy cập HTML thực tế
            # Ví dụ giả định cho các class MD5
            session_element = driver.find_element(By.CSS_SELECTOR, ".md5-session-id") 
            dice_elements = driver.find_elements(By.CSS_SELECTOR, ".md5-dice-item")
            
            session_id = session_element.text
            dices = [int(d.text) for d in dice_elements]
            current_total = sum(dices)
            current_res = "TAI" if current_total >= 11 else "XIU"

            # --- LOGIC TỰ ĐỘNG HỌC CẦU ---
            if session_id != data_store["last_session"]:
                # Nếu có phiên trước đó, cập nhật kết quả học
                if data_store["last_total"] is not None:
                    prev_score = str(data_store["last_total"])
                    data_store["history_learning"][prev_score]["count"] += 1
                    if current_res == "TAI":
                        data_store["history_learning"][prev_score]["tai"] += 1
                    else:
                        data_store["history_learning"][prev_score]["xiu"] += 1
                
                data_store["last_session"] = session_id
                data_store["last_total"] = current_total
                data_store["status"] = f"Đang quét bàn MD5 - Phiên: {session_id}"
                print(f"✅ Đã cập nhật phiên {session_id}: {current_total} ({current_res})")

        except Exception as e:
            data_store["status"] = "Đang chờ game tải hoặc lỗi Selector"
            print(f"⚠️ Warning: {e}")
        
        time.sleep(25) # Nghỉ theo chu kỳ game

# Chạy luồng quét ngầm
threading.Thread(target=monitor_md5_game, daemon=True).start()

@app.route('/api/data')
def get_data():
    results = []
    for score, data in data_store["history_learning"].items():
        rate = 0
        predict = "CHỜ"
        if data["count"] > 0:
            if data["tai"] >= data["xiu"]:
                rate = int((data["tai"] / data["count"]) * 100)
                predict = "TAI"
            else:
                rate = int((data["xiu"] / data["count"]) * 100)
                predict = "XIU"
        
        results.append({
            "score": score,
            "predict": predict,
            "rate": rate,
            "data_count": data["count"],
            "status": "MẠNH" if data["count"] > 5 else "ĐANG HỌC"
        })
        
    return jsonify({
        "phien_hien_tai": data_store["last_session"],
        "he_thong": data_store["status"],
        "predictions": results
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
