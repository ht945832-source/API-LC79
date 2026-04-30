# HOANGDZ MD5 AUTO-LEARNING API
Hệ thống API tự động quét kết quả và phân tích cầu MD5 hoàn toàn tự động.

## 🚀 Tính năng chính
- **Mắt ảo Selenium:** Tự động truy cập game, nhận diện bàn Tài Xỉu MD5 (màu tím/đỏ).
- **Auto-Learning:** Tự động học từ lịch sử phiên, tính toán tỷ lệ % dựa trên dữ liệu thực tế.
- **Không xâm nhập:** Hoạt động như một người dùng thật, giảm thiểu rủi ro bị khóa IP.
- **API Real-time:** Cung cấp dữ liệu dự đoán cho giao diện người dùng.

## 🛠 Hướng dẫn triển khai lên Render.com

### 1. Chuẩn bị
- Đưa toàn bộ các file này lên một kho lưu trữ (Repository) trên GitHub của bạn.

### 2. Cấu hình trên Render
- **Service Type:** Web Service
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python app.py`

### 3. Cài đặt Môi trường (Environment)
Để Selenium chạy được trên Render, bạn cần cài đặt Chrome. 
Vào phần **Settings** -> **Buildpacks**, thêm 2 link sau:
1. `https://github.com/heroku/heroku-buildpack-google-chrome`
2. `https://github.com/heroku/heroku-buildpack-chromedriver`

## 📊 Cấu trúc API
- `GET /api/data`: Lấy bảng dữ liệu dự đoán và trạng thái quét.
