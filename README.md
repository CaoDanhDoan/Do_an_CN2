# Đồ án Python cho Hệ Thống Nhúng: Nhà Thông Minh

## 🧠 Giới thiệu
Đề tài "Nhà Thông Minh" hướng đến việc xây dựng một hệ thống tự động hóa điều khiển các thiết bị trong nhà (đèn, quạt, cửa, cảm biến...) bằng công nghệ IoT. Hệ thống sử dụng ESP32, ESP32-CAM và ngôn ngữ Python, tích hợp WebServer và chatbot Telegram.
![Mô tả ảnh](Đồ án kì 1 năm 4(github)/Sanpham.png)
## 🎯 Mục tiêu
- Điều khiển thiết bị điện từ xa qua WebServer và Telegram
- Nhận diện khuôn mặt để mở cửa bằng ESP32-CAM
- Phát hiện khí gas, theo dõi nhiệt độ, độ ẩm, ánh sáng môi trường
- Hiển thị thông tin lên màn hình LCD/OLED
- Cảnh báo thông minh bằng còi (buzzer) và chatbot

## 🛠️ Công nghệ sử dụng
- **ESP32 & ESP32-CAM**
- **Python & C++**
- **Telegram Chatbot & WebServer**
- **MicroPython / Arduino IDE**
- **Module: Relay, Cảm biến khí MQ2, DHT11, ánh sáng, màn hình LCD/OLED, quạt 5V, khóa điện tử 12V**

## ⚙️ Tính năng hệ thống
- **Điều khiển thiết bị**: đèn, quạt, khóa cửa, qua cảm biến hoặc thủ công từ xa
- **Cảm biến thông minh**: khí gas, nhiệt độ/độ ẩm, ánh sáng
- **Cảnh báo**: buzzer hoặc tin nhắn Telegram khi phát hiện nguy hiểm
- **Nhận diện khuôn mặt**: mở cửa tự động bằng camera ESP32-CAM
- **Hiển thị thông tin**: qua màn hình hoặc WebServer

## 📡 Giao tiếp và Điều khiển
- Giao tiếp giữa các thiết bị qua UART, I2C
- WebServer ESP32 hiển thị trạng thái, điều khiển thiết bị
- Chatbot Telegram phản hồi và điều khiển từ người dùng

## 📐 Thiết kế hệ thống
- **Sơ đồ khối**: ESP32 làm trung tâm, thu nhận dữ liệu cảm biến → xử lý → điều khiển thiết bị → hiển thị → gửi dữ liệu lên WebServer hoặc Telegram
- **ESP32-CAM** nhận diện khuôn mặt → mở cửa nếu hợp lệ
- Các cảm biến gửi tín hiệu theo thời gian thực hoặc khi phát hiện bất thường
