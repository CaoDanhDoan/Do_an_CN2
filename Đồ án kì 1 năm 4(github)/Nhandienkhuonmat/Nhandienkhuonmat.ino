#include <WiFi.h>
#include <WiFiClientSecure.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "esp_camera.h"
#include <UniversalTelegramBot.h>
#include <ArduinoJson.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Wire.h>


const char* ssid = "DANH CAO";  //WiFi Name
const char* password = "12345678d";  //WiFi Password

String chatId = "-1002410210683";
String BOTtoken = "7553315989:AAHl1VDdCzPP3noX3A7TB0U0lPVW5FsLJ_A";

bool sendPhoto = false;

WiFiClientSecure clientTCP;

UniversalTelegramBot bot(BOTtoken, clientTCP);

// Define GPIOs
#define BUZZER_PIN 12  // Chân GPIO kết nối với buzzer
#define LOCK 13
#define FLASH_LED 4
#define BUTTON_PIN 2 

#define I2C_SDA 14 // Chân GPIO14 cho SDA
#define I2C_SCL 15 // Chân GPIO15 cho SCL
#define SCREEN_WIDTH 128 // Chiều rộng OLED
#define SCREEN_HEIGHT 64 // Chiều cao OLED
#define SSD1306_I2C_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

bool buzzerState = false; // Trạng thái của buzzer (bật hoặc tắt)
bool flashState = false;  // Trạng thái đèn flash (bật/tắt)
bool buttonTrackingEnabled = true;  // Biến cờ theo dõi nút bấm

//CAMERA_MODEL_AI_THINKER
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22


int lockState = 0;
String r_msg = "";
 
const unsigned long BOT_MTBS = 1000; // mean time between scan messages
unsigned long bot_lasttime; // last time messages' scan has been done

void handleNewMessages(int numNewMessages);
String sendPhotoTelegram();

String unlockDoor() {  
  if (lockState == 0) {
    digitalWrite(LOCK, LOW);
    lockState = 1;
    delay(100);
    digitalWrite(BUZZER_PIN, HIGH);  // Kích hoạt buzzer khi mở khóa
    delay(500);  // Buzzer kêu trong 500ms
    digitalWrite(BUZZER_PIN, LOW);   // Tắt buzzer
    //display.clearDisplay();
    //display.setCursor(0, 0);
    //display.println("Door\nUnlocked");
    //display.display();
    return "Door Unlocked. /lock";
  }
  else {
    return "Door Already Unlocked. /lock";
  }  
}
String lockDoor() {
  if (lockState == 1) {
    digitalWrite(LOCK, HIGH);
    lockState = 0;
    delay(100);
    digitalWrite(BUZZER_PIN, HIGH);  // Kích hoạt buzzer khi khóa cửa
    delay(500);  // Buzzer kêu trong 500ms
    digitalWrite(BUZZER_PIN, LOW);   // Tắt buzzer
    //display.clearDisplay();
    //display.setCursor(0, 0);
    //display.println("Door\nLocked");
    //display.display();
    return "Door Locked. /unlock";
  }
  else {
    return "Door Already Locked. /unlock";
  }
}

String sendPhotoTelegram(){
  const char* myDomain = "api.telegram.org";
  String getAll = "";
  String getBody = "";

  camera_fb_t * fb = NULL;
  fb = esp_camera_fb_get();  
  if(!fb) {
    Serial.println("Camera capture failed");
    delay(1000);
    ESP.restart();
    return "Camera capture failed";
  }  
  
  Serial.println("Connect to " + String(myDomain));

  if (clientTCP.connect(myDomain, 443)) {
    Serial.println("Connection successful");
    
   Serial.println("Connected to " + String(myDomain));
    
    String head = "--IotCircuitHub\r\nContent-Disposition: form-data; name=\"chat_id\"; \r\n\r\n" + chatId + "\r\n--IotCircuitHub\r\nContent-Disposition: form-data; name=\"photo\"; filename=\"esp32-cam.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n";
    String tail = "\r\n--IotCircuitHub--\r\n";

    uint16_t imageLen = fb->len;
    uint16_t extraLen = head.length() + tail.length();
    uint16_t totalLen = imageLen + extraLen;
  
    clientTCP.println("POST /bot"+BOTtoken+"/sendPhoto HTTP/1.1");
    clientTCP.println("Host: " + String(myDomain));
    clientTCP.println("Content-Length: " + String(totalLen));
    clientTCP.println("Content-Type: multipart/form-data; boundary=IotCircuitHub");
    clientTCP.println();
    clientTCP.print(head);
  
    uint8_t *fbBuf = fb->buf;
    size_t fbLen = fb->len;
    for (size_t n=0;n<fbLen;n=n+1024) {
      if (n+1024<fbLen) {
        clientTCP.write(fbBuf, 1024);
        fbBuf += 1024;
      }
      else if (fbLen%1024>0) {
        size_t remainder = fbLen%1024;
        clientTCP.write(fbBuf, remainder);
      }
    }  
    
    clientTCP.print(tail);
    
    esp_camera_fb_return(fb);
    
    int waitTime = 10000;   // timeout 10 seconds
    long startTimer = millis();
    boolean state = false;
    
    while ((startTimer + waitTime) > millis()){
      Serial.print(".");
      delay(100);      
      while (clientTCP.available()){
          char c = clientTCP.read();
          if (c == '\n'){
            if (getAll.length()==0) state=true; 
            getAll = "";
          } 
          else if (c != '\r'){
            getAll += String(c);
          }
          if (state==true){
            getBody += String(c);
          }
          startTimer = millis();
       }
       if (getBody.length()>0) break;
    }
    clientTCP.stop();
    Serial.println(getBody);
  }
  else {
    getBody="Connected to api.telegram.org failed.";
    Serial.println("Connected to api.telegram.org failed.");
  }
  return getBody;
}

void handleNewMessages(int numNewMessages){
  Serial.print("Handle New Messages: ");
  Serial.println(numNewMessages);

  for (int i = 0; i < numNewMessages; i++){
    // Chat id of the requester
    String chat_id = String(bot.messages[i].chat_id);
    if (chat_id != chatId){
      bot.sendMessage(chat_id, "Unauthorized user", "");
      continue;
    }
    
    // Print the received message
    String text = bot.messages[i].text;
    Serial.println(text);

    String fromName = bot.messages[i].from_name;
    String oledMessage = ""; // Nội dung hiển thị trên OLED
    if (text == "/flash") {
      flashState = !flashState;  // Đảo ngược trạng thái của đèn flash
      digitalWrite(FLASH_LED, flashState ? HIGH : LOW);  // Bật/tắt đèn flash

      oledMessage = flashState ? "Flash On" : "Flash Off";  // Cập nhật trạng thái đèn flash trên OLED
      bot.sendMessage(chatId, oledMessage, "");
    }
    if (text == "/button") {
      buttonTrackingEnabled = !buttonTrackingEnabled;  // Đảo ngược trạng thái theo dõi nút bấm

      String buttonStateMessage = buttonTrackingEnabled ? "Button tracking enabled." : "Button tracking disabled.";
      oledMessage = buttonStateMessage;
      bot.sendMessage(chatId, buttonStateMessage, "");
    }
    if (text == "/photo") {
      sendPhoto = true;
      oledMessage = "Taking photo...";
      Serial.println("New photo request");
    }
    if (text == "/lock"){
      String r_msg = lockDoor();
      bot.sendMessage(chatId, r_msg, "");
      oledMessage = "Door\nlocked";
    }
    if (text == "/unlock"){
      String r_msg = unlockDoor();
      bot.sendMessage(chatId, r_msg, "");
      oledMessage = "Door\hUnlocked";
    }
    if (text == "/start"){
      String welcome = "Welcome to my home.\n";
      welcome += "/photo : Takes a new photo\n";
      welcome += "/buzzer : Danger warning\n";
      welcome += "/unlock : Unlock the Door\n";
      welcome += "/lock : Lock the Door\n";
      welcome += "/flash : Danger warning\n";
      welcome += "/button : Toggle button tracking\n";
      welcome += "To get the photo please tap on /photo.\n";
      bot.sendMessage(chatId, welcome, "Markdown");
    }
     if (text == "/buzzer") {
      if (buzzerState) {
        digitalWrite(BUZZER_PIN, LOW);  // Tắt buzzer nếu buzzer đã bật
        buzzerState = false;
        bot.sendMessage(chatId, "Buzzer turned off.", "");
        oledMessage = "Buzzer Off";
      } else {
        digitalWrite(BUZZER_PIN, HIGH); // Bật buzzer
        delay(2000);  // Buzzer kêu trong 500ms
        digitalWrite(BUZZER_PIN, LOW);  // Tắt buzzer
        buzzerState = true;
        bot.sendMessage(chatId, "Buzzer turned on.", "");
        oledMessage = "Buzzer On";

      }
  }
  // Hiển thị trạng thái lên OLED
    display.clearDisplay();
    display.setCursor(0, 0);
    display.print("Telegram:");
    display.setCursor(0, 16);
    display.print(oledMessage);
    display.display();

}
}

void setup(){
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); 
  Serial.begin(115200);
  delay(1000);

  // Khởi tạo OLED
  Wire.begin(I2C_SDA, I2C_SCL);
  if (!display.begin(SSD1306_I2C_ADDRESS, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println(F("Welcome to Smart Home")); // Dòng chào mừng đầu tiên
  display.setCursor(0, 16);
  display.println(F("System Initializing...")); // Dòng thông báo hệ thống
  display.setCursor(0, 32);
  display.println(F("Please Wait..."));         // Dòng chờ khởi động
  display.display();
  delay(2000);

  pinMode(LOCK,OUTPUT);
  pinMode(FLASH_LED,OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  digitalWrite(LOCK, LOW);
  
  WiFi.mode(WIFI_STA);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password); 
  clientTCP.setCACert(TELEGRAM_CERTIFICATE_ROOT); 
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.print("ESP32-CAM IP Address: ");
  Serial.println(WiFi.localIP());

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  //init with high specs to pre-allocate larger buffers
  if(psramFound()){
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;  //0-63 lower number means higher quality
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;  //0-63 lower number means higher quality
    config.fb_count = 1;
  }
  
  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    delay(1000);
    ESP.restart();
  }

  // Drop down frame size for higher initial frame rate
  sensor_t * s = esp_camera_sensor_get();
  s->set_framesize(s, FRAMESIZE_CIF);  // UXGA|SXGA|XGA|SVGA|VGA|CIF|QVGA|HQVGA|QQVGA
}

void loop(){
  static bool lastButtonState = HIGH;  // Trạng thái nút bấm trước
  bool currentButtonState = digitalRead(BUTTON_PIN);  // Đọc trạng thái nút bấm

  if (currentButtonState == LOW && lastButtonState == HIGH) {  // Khi nút bấm được nhấn
    Serial.println("Button pressed! Triggering doorbell...");
    
    // Kích hoạt buzzer
    digitalWrite(BUZZER_PIN, HIGH);
    delay(500);  // Buzzer kêu trong 500ms
    digitalWrite(BUZZER_PIN, LOW);
    
    // Chụp ảnh và gửi qua Telegram
    digitalWrite(FLASH_LED, HIGH);  // Bật đèn flash
    delay(200);
    sendPhotoTelegram();  // Chụp và gửi ảnh
    digitalWrite(FLASH_LED, LOW);  // Tắt đèn flash
  }
  
  lastButtonState = currentButtonState;  // Cập nhật trạng thái nút bấm

    
  if (sendPhoto){
    Serial.println("Preparing photo");
    digitalWrite(FLASH_LED, HIGH);
    delay(200);
    sendPhotoTelegram(); 
    digitalWrite(FLASH_LED, LOW);
    sendPhoto = false; 
  }

  if (millis() - bot_lasttime > BOT_MTBS)
  {
    int numNewMessages = bot.getUpdates(bot.last_message_received + 1);

    while (numNewMessages)
    {
      Serial.println("got response");
      handleNewMessages(numNewMessages);
      numNewMessages = bot.getUpdates(bot.last_message_received + 1);
    }
    bot_lasttime = millis();
  }
}