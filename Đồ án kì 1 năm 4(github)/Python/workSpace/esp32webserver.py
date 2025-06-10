



import socket
from machine import Pin, I2C, ADC
from time import sleep
from i2c_lcd import I2cLcd  
import dht
# Khởi tạo I2C và LCD
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)  # GPIO 22 (SCL), GPIO 21 (SDA)
lcd = I2cLcd(i2c, i2c_addr=0x27, num_lines=2, num_columns=16)
# Khởi tạo các relay
relay1 = Pin(5, Pin.OUT)  # Relay 1
relay2 = Pin(14, Pin.OUT)  # Relay 2
relay3 = Pin(19, Pin.OUT) # Relay 3

dht_pin = Pin(4)
dht_sensor = dht.DHT11(dht_pin)
# Set trạng thái ban đầu của relay (OFF)
relay1.value(1)  # Relay inactive (active low)
relay2.value(1)
relay3.value(1)
# Khởi tạo chân ADC cho cảm biến khí gas MQ-2
mq2_pin = ADC(Pin(33))  
mq2_pin.atten(ADC.ATTN_11DB)  # Thiết lập độ khuếch đại cho ADC

# Thiết lập chân cảm biến ánh sáng và chân LED
sensor_pin = ADC(Pin(35))  
sensor_pin.atten(ADC.ATTN_11DB)  # Thiết lập độ khuếch đại ADC
led_pin = Pin(32, Pin.OUT)  # GPIO32 cho đèn LED
# Khởi tạo Buzzer


buzzer = Pin(27, Pin.OUT)  # Buzzer nối với GPIO 27

# Ngưỡng nhiệt độ và khí gas
TEMP_THRESHOLD = 30  # Nhiệt độ vượt quá 30°C sẽ cảnh báo
GAS_THRESHOLD = 2000  # Giá trị cảm biến khí gas MQ-2
# Ngưỡng ánh sáng để bật/tắt đèn
threshold = 2000

# Biến điều khiển chế độ tự động bật đèn
auto_mode = True

def read_mq2():
    # Đọc giá trị từ cảm biến MQ-2
    mq2_value = mq2_pin.read()  # Giá trị đọc từ cảm biến (0-4095)


    return mq2_value


def read_dht():
    global temp, hum
    temp = hum = 0
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        if isinstance(temp, (float, int)) and isinstance(hum, (float, int)):
            return b'{0:3.1f},{1:3.1f}'.format(temp, hum)
        else:
            return 'Invalid sensor readings.'
    except OSError as e:
        return 'Failed to read sensor.'
def check_temperature_and_gas():
    global temp  # Biến nhiệt độ toàn cục
    gas_value = read_mq2()  # Đọc giá trị từ cảm biến MQ-2
    
    print(f"Temp: {temp}, MQ-2: {gas_value}")  # In giá trị kiểm tra
    
    if temp > TEMP_THRESHOLD or gas_value > GAS_THRESHOLD:
        print("Warning: Temp or Gas exceeds threshold!")
        # Bật relay và buzzer
        relay3.value(0)  # Bật relay3 
        buzzer.on()      # Bật buzzer
        return True
    else:
        print("All normal. Temp and Gas are safe.")  
        # Tắt relay và buzzer
        relay3.value(1)  # Tắt relay3 
        buzzer.off()     # Tắt buzzer
        return False

def web_page():
    mq2_value = read_mq2()
     # Kiểm tra nếu có cảnh báo nhiệt độ hoặc khí gas
    warning = check_temperature_and_gas()
    warning_message = ""
    if warning:
        warning_message = "<p style='color:red;'>Warning: High Temperature or Gas Level!</p>"
    return """<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TEMPERATURE & HUMIDITY</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f7fb;
            color: #333;
            margin: 0;
            padding: 0;
            text-align: center;
        }
        .container {
            margin-top: 30px;
            padding: 20px;
            background-color: #ffffff;
            width: 90%;
            max-width: 600px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        h1 {
            font-size: 2rem;
            color: #007bff;
            margin-bottom: 20px;
        }
        .sensor-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
        }
        .sensor-card {
            width: 45%;
            padding: 15px;
            background-color: #e9f3ff;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        .sensor-card p {
            font-size: 1.5rem;
            margin: 0;
            color: #333;
        }
        .sensor-bar {
            width: 100%;
            height: 10px;
            border-radius: 5px;
            background-color: #e4e4e4;
            margin-top: 10px;
        }
        .progress-bar {
            height: 100%;
            border-radius: 5px;
        }
        .progress-bar-temp {
            background: linear-gradient(to top, #f44336 0%, #ffeb3b 100%);
        }
        .progress-bar-hum {
            background: linear-gradient(to top, #03a9f4 0%, #4caf50 100%);
        }
        .footer {
            margin-top: 30px;
            font-size: 0.8rem;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Temperature & Humidity</h1>
        """ + warning_message + """ <!-- Show warning message if condition is met -->  
        <!-- Display Temperature -->
        <div class="sensor-container">
            <div class="sensor-card">
                <p>Temperature</p>
                <p><strong>""" + str(temp) + """ &deg;C</strong></p>
                <div class="sensor-bar">
                    <div class="progress-bar progress-bar-temp" style="width: """ + str(temp) + """%;"></div>
                </div>
            </div>
        
        <!-- Display Humidity -->
            <div class="sensor-card">
                <p>Humidity</p>
                <p><strong>""" + str(hum) + """ %</strong></p>
                <div class="sensor-bar">
                    <div class="progress-bar progress-bar-hum" style="width: """ + str(hum) + """%;"></div>
                </div>
            </div>
        <!-- Display Gas Level -->
            <div class="sensor-card">
                <p>Gas Level (MQ-2)</p>
                <p><strong>""" + str(mq2_value) + """</strong></p>
                <div class="sensor-bar">
                    <div class="progress-bar progress-bar-hum" style="width: """ + str(mq2_value // 40) + """%;"></div>
                </div>
            </div>
        </div>
    </div>
</body>

</html>
"""


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
            align-items: center.
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
            transition: background-color 0.3s ease, transform 0.2s ease.
        }

        .button.on {
            background-color: #28a745;
            color: white.
        }

        .button.on:hover {
            background-color: #218838;
            transform: scale(1.05).
        }

        .button.off {
            background-color: #dc3545;
            color: white.
        }

        .button.off:hover {
            background-color: #c82333;
            transform: scale(1.05).
        }

        /* Footer */
        footer {
            margin-top: 20px.
            font-size: 0.9em.
            color: #6c757d.
        }

        footer a {
            color: #007bff.
            text-decoration: none.
        }

        footer a:hover {
            text-decoration: underline.
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>HOME AUTOMATION</h1>
        <!-- Relay 1 -->
        <div class="relay-card">
            <h3>LED 1</h3>
            <div class="buttons">

                <a href="/?relay1=on"><button class="button on">ON</button></a>
                <a href="/?relay1=off"><button class="button off">OFF</button></a>
            </div>
        </div>
        <!-- Relay 2 -->
        <div class="relay-card">
            <h3>LED 2</h3>
            <div class="buttons">
                <a href="/?relay2=on"><button class="button on">ON</button></a>
                <a href="/?relay2=off"><button class="button off">OFF</button></a>
            </div>
        </div>
        <!-- Relay 3 -->
        <div class="relay-card">
            <h3>FAN</h3>
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
# Hiển thị tin nhắn

lcd.clear()
lcd.putstr("HOME AUTOMATION\nSYSTEM READY")

# Cấu hình socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 80))
s.listen(5)

def read_dht_and_display():
    try:
        dht_sensor.measure()  # Đọc dữ liệu từ DHT11
        temp = dht_sensor.temperature()  # Lấy nhiệt độ
        humidity = dht_sensor.humidity()  # Lấy độ ẩm
        mq2_value = read_mq2()
        print("Nhiet do:", temp, "°C")
        print("Do am:", humidity, "%")
        print("Gas Level:", mq2_value)

        # Hiển thị dữ liệu lên LCD
        lcd.clear()
        lcd.putstr("Nhiet do: {}C\nDo am: {}%\nGas: {}".format(temp, humidity, mq2_value))
    except OSError as e:
        print("Lỗi đọc DHT11:", e)

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
        relay1.value(0)  # Bật relay
        print("Relay 1 ON")
        lcd.clear()
        lcd.putstr("Relay 1: ON")
    if relay1_off != -1:
        relay1.value(1)  # Tắt relay
        print("Relay 1 OFF")
        lcd.clear()
        lcd.putstr("Relay 1: OFF")

    if relay2_on != -1:
        relay2.value(0)  # Bật relay
        print("Relay 2 ON")
        lcd.clear()
        lcd.putstr("Relay 2: ON")
    if relay2_off != -1:
        relay2.value(1)  # Tắt relay
        print("Relay 2 OFF")
        lcd.clear()
        lcd.putstr("Relay 2: OFF")

    if relay3_on != -1:
        relay3.value(0)  # Bật relay
        print("Relay 3 ON")
        lcd.clear()
        lcd.putstr("Relay 3: ON")
    if relay3_off != -1:
        relay3.value(1)  # Tắt relay
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
        lcd.putstr("LED: ON")
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
def read_light_sensor():
    readings = []
    for _ in range(5):  # Đọc giá trị nhiều lần để lấy trung bình
        readings.append(sensor_pin.read())
        sleep(0.01)
    average_value = sum(readings) // len(readings)  # Tính trung bình
    return average_value

while True:
    # Đọc giá trị cảm biến ánh sáng
    sensor_value = read_light_sensor()
    print("Gia tri cam bien:", sensor_value)
    
    read_dht_and_display()
    sleep(3)

    # Bật/tắt đèn LED dựa trên giá trị cảm biến nếu chế độ tự động bật
    if auto_mode:
        if sensor_value > threshold:
            led_pin.on()  # Bật đèn LED
        else:
            led_pin.off()  # Tắt đèn LED
    
    # Chấp nhận kết nối client  
    s.settimeout(0.1)  # Giảm thời gian chờ của socket
    try:
        cs, addr = s.accept()
        request = cs.recv(1024)
        request = str(request)
        sensor_readings = read_dht()
        response = web_page()
        handle_relays(request)
        handle_led(request)        
        cs.send('HTTP/1.1 200 OK\n')
        cs.send('Content-Type: text/html\n')
        cs.send('Connection: close\n\n')
        # Gửi trang HTML tới client
        cs.sendall(response)
        cs.send(html)
        cs.close()
    except:
        pass  
    sleep(3)


