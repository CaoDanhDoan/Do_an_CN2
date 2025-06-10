import socket
from machine import Pin, I2C, ADC
from time import sleep
from i2c_lcd import I2cLcd  

# Khởi tạo I2C và LCD
i2c = I2C(0, scl=Pin(23), sda=Pin(21), freq=400000)  # GPIO 23 (SCL), GPIO 21 (SDA)
lcd = I2cLcd(i2c, i2c_addr=0x27, num_lines=2, num_columns=16)

# Khởi tạo các relay
relay1 = Pin(5, Pin.OUT)  # Relay 1
relay2 = Pin(4, Pin.OUT)  # Relay 2
relay3 = Pin(14, Pin.OUT) # Relay 3

# Set trạng thái ban đầu của relay (OFF)
relay1.value(1)  # Relay inactive (active low)
relay2.value(1)
relay3.value(1)

# Thiết lập chân cảm biến ánh sáng và chân LED
sensor_pin = ADC(Pin(34))  # GPIO34 cho cảm biến ánh sáng
sensor_pin.atten(ADC.ATTN_11DB)  # Thiết lập độ khuếch đại ADC
led_pin = Pin(32, Pin.OUT)  # GPIO32 cho đèn LED

# Ngưỡng ánh sáng để bật/tắt đèn
threshold = 500  

# Biến điều khiển chế độ tự động bật đèn
auto_mode = True

# Giao diện HTML
html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MICROPYTHON WITH ESP 32</title>
    <style>
        /* Reset CSS */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        /* Body Style */
        body {
            font-family: 'Roboto', Arial, sans-serif;
            background-color: #f5f7fa;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        /* Main Container */
        .container {
            background: #ffffff;
            padding: 20px;
            max-width: 700px;
            width: 100%;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        /* Header */
        h1 {
            font-size: 2em;
            margin-bottom: 20px;
            color: #007bff;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        /* Relay Card */
        .relay-card {
            background: #f9fafc;
            padding: 15px 20px;
            margin: 15px 0;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .relay-card h3 {
            font-size: 1.2em;
            margin: 0;
            color: #333;
        }

        /* Buttons */
        .buttons {
            display: flex;
            gap: 10px;
        }

        .button {
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }

        .button.on {
            background-color: #28a745;
            color: white;
        }

        .button.on:hover {
            background-color: #218838;
            transform: scale(1.05);
        }

        .button.off {
            background-color: #dc3545;
            color: white;
        }

        .button.off:hover {
            background-color: #c82333;
            transform: scale(1.05);
        }

        /* Footer */
        footer {
            margin-top: 20px;
            font-size: 0.9em;
            color: #6c757d;
        }

        footer a {
            color: #007bff;
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>HOME AUTOMATION</h1>
        <!-- Relay 1 -->
        <div class="relay-card">
            <h3>Relay 1</h3>
            <div class="buttons">
                <a href="/?relay1=on"><button class="button on">ON</button></a>
                <a href="/?relay1=off"><button class="button off">OFF</button></a>
            </div>
        </div>
        <!-- Relay 2 -->
        <div class="relay-card">
            <h3>Relay 2</h3>
            <div class="buttons">
                <a href="/?relay2=on"><button class="button on">ON</button></a>
                <a href="/?relay2=off"><button class="button off">OFF</button></a>
            </div>
        </div>
        <!-- Relay 3 -->
        <div class="relay-card">
            <h3>Relay 3</h3>
            <div class="buttons">
                <a href="/?relay3=on"><button class="button on">ON</button></a>
                <a href="/?relay3=off"><button class="button off">OFF</button></a>
            </div>
        </div>
        <!-- LED Control -->
        <div class="relay-card">
            <h3>LED</h3>
            <div class="buttons">
                <a href="/?led=on"><button class="button on">ON</button></a>
                <a href="/?led=off"><button class="button off">OFF</button></a>
            </div>
        </div>
        <!-- Auto Mode Control -->
        <div class="relay-card">
            <h3>Auto Mode</h3>
            <div class="buttons">
                <a href="/?auto=on"><button class="button on">ON</button></a>
                <a href="/?auto=off"><button class="button off">OFF</button></a>
            </div>
        </div>
        <footer>
            Doan Cao Danh 
        </footer>
    </div>
</body>
</html>
"""

# Hiển thị tin nhắn khởi động trên LCD
lcd.clear()
lcd.putstr("Relay Control\nSystem Ready")

# Cấu hình socket
s = socket.socket()
s.bind(('0.0.0.0', 80))
s.listen(5)

def handle_relays(request):
    # Tìm lệnh điều khiển relay trong request
    relay1_on = request.find('/?relay1=on')
    relay1_off = request.find('/?relay1=off')
    relay2_on = request.find('/?relay2=on')
    relay2_off = request.find('/?relay2=off')
    relay3_on = request.find('/?relay3=on')
    relay3_off = request.find('/?relay3=off')

    # Điều khiển relay và cập nhật LCD
    if relay1_on != -1:
        relay1.value(0)
        print("Relay 1 ON")
        lcd.clear()
        lcd.putstr("Relay 1: ON")
    if relay1_off != -1:
        relay1.value(1)
        print("Relay 1 OFF")
        lcd.clear()
        lcd.putstr("Relay 1: OFF")

    if relay2_on != -1:
        relay2.value(0)
        print("Relay 2 ON")
        lcd.clear()
        lcd.putstr("Relay 2: ON")
    if relay2_off != -1:
        relay2.value(1)
        print("Relay 2 OFF")
        lcd.clear()
        lcd.putstr("Relay 2: OFF")

    if relay3_on != -1:
        relay3.value(0)
        print("Relay 3 ON")
        lcd.clear()
        lcd.putstr("Relay 3: ON")
    if relay3_off != -1:
        relay3.value(1)
        print("Relay 3 OFF")
        lcd.clear()
        lcd.putstr("Relay 3: OFF")

def handle_led(request):
    # Tìm lệnh điều khiển LED trong request
    led_on = request.find('/?led=on')
    led_off = request.find('/?led=off')
    auto_on = request.find('/?auto=on')
    auto_off = request.find('/?auto=off')

    global auto_mode  # Khai báo biến auto_mode để sử dụng trong hàm

    # Điều khiển LED và cập nhật LCD
    if led_on != -1:
        led_pin.on()
        auto_mode = True  # Bật chế độ tự động khi LED được bật thủ công
        print("LED ON - Auto Mode Enabled")
        lcd.clear()
        lcd.putstr("LED: ON\nAuto Mode: ON")
    if led_off != -1:
        led_pin.off()
        auto_mode = False  # Tắt chế độ tự động khi LED được tắt thủ công
        print("LED OFF - Auto Mode Disabled")
        lcd.clear()
        lcd.putstr("LED: OFF\nAuto Mode: OFF")
    if auto_on != -1:
        auto_mode = True
        print("Auto Mode ON")
        lcd.clear()
        lcd.putstr("Auto Mode: ON")
    if auto_off != -1:
        auto_mode = False
        print("Auto Mode OFF")
        lcd.clear()
        lcd.putstr("Auto Mode: OFF")

while True:
    # Đọc giá trị cảm biến ánh sáng
    sensor_value = sensor_pin.read()
    print("Giá trị cảm biến:", sensor_value)
    
    # Bật/tắt đèn LED dựa trên giá trị cảm biến nếu chế độ tự động bật
    if auto_mode:
        if sensor_value < threshold:
            led_pin.on()  # Bật đèn LED
        else:
            led_pin.off()  # Tắt đèn LED
    
    # Chấp nhận kết nối client
    s.settimeout(0.1)  # Giảm thời gian chờ của socket
    try:
        cs, addr = s.accept()
        request = cs.recv(1024)
        request = str(request)
        handle_relays(request)
        handle_led(request)
        # Gửi trang HTML tới client
        cs.send(html)
        cs.close()
    except:
        pass  
    sleep(3)


