import network
import time

# Khởi tạo đối tượng WiFi
w = network.WLAN(network.STA_IF)

# Bật WiFi
w.active(True)

# Kết nối đến mạng WiFi
w.connect("Hí lô", "12345678d")

# Kiểm tra trạng thái kết nối và chờ cho đến khi kết nối thành công
while not w.isconnected():
    print("Đang kết nối...")
    time.sleep(1)

# In ra địa chỉ IP
print("Địa chỉ IP là", w.ifconfig()[0])

