/**
 * AI Dynamic Painting System - Phase 1
 * M5STACK Basic/Gray Controller (物理ボタン版)
 * 
 * Arduino IDE用 .inoファイル
 * M5Stack Basic/Gray用に修正
 */

#include <M5Stack.h>  // M5Core2.h ではなく M5Stack.h を使用！
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ===== 設定項目 (ここを変更してください) =====
const char* WIFI_SSID = "makotaronet";        // WiFi SSID
const char* WIFI_PASSWORD = "Makotaro0731Syunpeman0918"; // WiFi パスワード
const char* API_BASE_URL = "http://192.168.10.7:8000"; // Raspberry Pi IP
// ==========================================

// Global variables
bool wifiConnected = false;
String currentVideoId = "";
String playbackStatus = "idle";
unsigned long lastApiCheck = 0;
const unsigned long API_CHECK_INTERVAL = 5000;  // Check API every 5 seconds

// Function declarations
void setupWiFi();
void updateDisplay();
void handleButtons();
void checkApiStatus();
void sendControlCommand(String command);

void setup() {
    // Initialize M5Stack Basic/Gray
    M5.begin(true, false, true);  // LCD, SD, Serial
    M5.Power.begin();
    
    M5.Lcd.setTextSize(2);
    M5.Lcd.setTextColor(WHITE, BLACK);
    
    // Display startup message
    M5.Lcd.clear();
    M5.Lcd.setCursor(10, 10);
    M5.Lcd.println("AI Dynamic Painting");
    M5.Lcd.println("Phase 1 - Initializing...");
    
    Serial.begin(115200);
    Serial.println("=== AI Dynamic Painting M5STACK Basic ===");
    
    // Setup WiFi
    setupWiFi();
    
    // Initialize buttons
    M5.Lcd.setCursor(10, 200);
    M5.Lcd.setTextSize(1);
    M5.Lcd.println("A: Play/Pause  B: Stop  C: Next");
}

void loop() {
    M5.update();  // Update button states
    
    // Handle button presses
    handleButtons();
    
    // Check API status periodically
    if (millis() - lastApiCheck > API_CHECK_INTERVAL) {
        checkApiStatus();
        lastApiCheck = millis();
    }
    
    // Update display
    updateDisplay();
    
    delay(100);  // Small delay to prevent excessive CPU usage
}

void setupWiFi() {
    M5.Lcd.setCursor(10, 50);
    M5.Lcd.println("Connecting to WiFi...");
    Serial.print("Connecting to ");
    Serial.println(WIFI_SSID);
    Serial.println("Target BSSID: A4:12:42:9E:22:72");
    
    // 特定のルーター(Raspberry Piと同じ)に接続
    uint8_t bssid[6] = {0xA4, 0x12, 0x42, 0x9E, 0x22, 0x72};
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD, 0, bssid, true);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        M5.Lcd.print(".");
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        wifiConnected = true;
        M5.Lcd.println("\nWiFi Connected!");
        M5.Lcd.print("IP: ");
        M5.Lcd.println(WiFi.localIP());
        Serial.println("\nWiFi Connected!");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
        Serial.print("Connected to BSSID: ");
        Serial.println(WiFi.BSSIDstr());
        
        // Display API server info
        M5.Lcd.print("API: ");
        M5.Lcd.println(API_BASE_URL);
        Serial.print("API Server: ");
        Serial.println(API_BASE_URL);
    } else {
        M5.Lcd.println("\nWiFi Connection Failed!");
        Serial.println("\nWiFi Connection Failed!");
        wifiConnected = false;
    }
    
    delay(2000);
}

void updateDisplay() {
    static unsigned long lastUpdate = 0;
    
    // Update display every second
    if (millis() - lastUpdate < 1000) {
        return;
    }
    lastUpdate = millis();
    
    // Clear display area
    M5.Lcd.fillRect(0, 70, 320, 120, BLACK);
    
    // Display connection status
    M5.Lcd.setCursor(10, 70);
    M5.Lcd.setTextSize(2);
    
    if (!wifiConnected) {
        M5.Lcd.setTextColor(RED, BLACK);
        M5.Lcd.println("WiFi Disconnected");
    } else {
        M5.Lcd.setTextColor(GREEN, BLACK);
        M5.Lcd.println("System Online");
        
        // Display playback status
        M5.Lcd.setCursor(10, 100);
        M5.Lcd.setTextColor(WHITE, BLACK);
        M5.Lcd.print("Status: ");
        
        if (playbackStatus == "playing") {
            M5.Lcd.setTextColor(GREEN, BLACK);
            M5.Lcd.println("Playing");
        } else if (playbackStatus == "paused") {
            M5.Lcd.setTextColor(YELLOW, BLACK);
            M5.Lcd.println("Paused");
        } else {
            M5.Lcd.setTextColor(WHITE, BLACK);
            M5.Lcd.println("Idle");
        }
        
        // Display current video info
        if (!currentVideoId.isEmpty()) {
            M5.Lcd.setCursor(10, 130);
            M5.Lcd.setTextColor(WHITE, BLACK);
            M5.Lcd.setTextSize(1);
            M5.Lcd.print("Video: ");
            M5.Lcd.println(currentVideoId);
        }
    }
    
    // Restore button labels
    M5.Lcd.setCursor(10, 200);
    M5.Lcd.setTextSize(1);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.println("A: Play/Pause  B: Stop  C: Next");
}

void handleButtons() {
    // Button A: Play/Pause (物理ボタン用)
    if (M5.BtnA.wasReleased()) {  // wasPressed → wasReleased に変更
        M5.Lcd.fillRect(0, 160, 320, 20, BLACK);
        M5.Lcd.setCursor(10, 160);
        M5.Lcd.setTextColor(YELLOW, BLACK);
        
        if (playbackStatus == "playing") {
            M5.Lcd.println("Sending: Pause");
            Serial.println("Button A: Sending Pause");
            sendControlCommand("play_pause");
        } else {
            M5.Lcd.println("Sending: Play");
            Serial.println("Button A: Sending Play");
            sendControlCommand("play_pause");
        }
    }
    
    // Button B: Stop
    if (M5.BtnB.wasReleased()) {
        M5.Lcd.fillRect(0, 160, 320, 20, BLACK);
        M5.Lcd.setCursor(10, 160);
        M5.Lcd.setTextColor(YELLOW, BLACK);
        M5.Lcd.println("Sending: Stop");
        Serial.println("Button B: Sending Stop");
        sendControlCommand("stop");
    }
    
    // Button C: Next Video
    if (M5.BtnC.wasReleased()) {
        M5.Lcd.fillRect(0, 160, 320, 20, BLACK);
        M5.Lcd.setCursor(10, 160);
        M5.Lcd.setTextColor(YELLOW, BLACK);
        M5.Lcd.println("Sending: Next");
        Serial.println("Button C: Sending Next");
        sendControlCommand("next");
    }
}

void checkApiStatus() {
    if (!wifiConnected) {
        return;
    }
    
    HTTPClient http;
    String url = String(API_BASE_URL) + "/api/display/status";
    
    Serial.print("Checking API status: ");
    Serial.println(url);
    
    http.begin(url);
    int httpCode = http.GET();
    
    if (httpCode == 200) {
        String payload = http.getString();
        Serial.print("API Response: ");
        Serial.println(payload);
        
        // Parse JSON response
        DynamicJsonDocument doc(1024);
        DeserializationError error = deserializeJson(doc, payload);
        
        if (!error) {
            // Update status from API response
            if (doc.containsKey("session") && !doc["session"].isNull()) {
                playbackStatus = doc["session"]["playback_status"].as<String>();
                currentVideoId = doc["session"]["video_id"].as<String>();
            } else {
                playbackStatus = "idle";
                currentVideoId = "";
            }
        } else {
            Serial.print("JSON Parse Error: ");
            Serial.println(error.c_str());
        }
    } else {
        Serial.print("HTTP Error: ");
        Serial.println(httpCode);
    }
    
    http.end();
}

void sendControlCommand(String command) {
    if (!wifiConnected) {
        M5.Lcd.setCursor(10, 180);
        M5.Lcd.setTextColor(RED, BLACK);
        M5.Lcd.println("Error: No WiFi");
        Serial.println("Error: No WiFi connection");
        return;
    }
    
    HTTPClient http;
    String url = String(API_BASE_URL) + "/api/m5stack/control";
    
    Serial.print("Sending command to: ");
    Serial.println(url);
    
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    
    // Create JSON payload with device_info
    String jsonPayload = "{\"action\":\"" + command + "\",\"device_info\":{\"device_id\":\"m5stack-001\"}}";
    Serial.print("Payload: ");
    Serial.println(jsonPayload);
    
    int httpCode = http.POST(jsonPayload);
    
    M5.Lcd.fillRect(0, 180, 320, 20, BLACK);
    M5.Lcd.setCursor(10, 180);
    
    if (httpCode == 200) {
        M5.Lcd.setTextColor(GREEN, BLACK);
        M5.Lcd.println("Command sent successfully");
        Serial.println("Command sent successfully");
        
        // Update local status based on command
        if (command == "play") {
            playbackStatus = "playing";
        } else if (command == "pause") {
            playbackStatus = "paused";
        } else if (command == "stop") {
            playbackStatus = "idle";
            currentVideoId = "";
        }
    } else {
        M5.Lcd.setTextColor(RED, BLACK);
        M5.Lcd.print("Error: HTTP ");
        M5.Lcd.println(httpCode);
        Serial.print("HTTP Error: ");
        Serial.println(httpCode);
    }
    
    http.end();
}