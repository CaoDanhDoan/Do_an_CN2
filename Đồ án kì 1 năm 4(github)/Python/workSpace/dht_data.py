import json

def handle_dht_data():
    # Đọc dữ liệu từ cảm biến DHT
    sensor_data = read_dht()  # Bạn có thể sửa lại hàm này để trả về dữ liệu theo định dạng cần thiết
    if sensor_data:
        temp, hum = map(float, sensor_data.split(','))
        return json.dumps({'temperature': temp, 'humidity': hum})
    else:
        return json.dumps({'error': 'Failed to read sensor'})

# Xử lý yêu cầu HTTP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    print('Content = %s' % str(request))

    # Kiểm tra yêu cầu API
    if '/dht_data' in str(request):
        response = handle_dht_data()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: application/json\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
    else:
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)

    conn.close()

