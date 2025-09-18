/**
 * M5STACK Core2 Firmware - Phase 1
 * T050: Basic communication with Raspberry Pi API
 * 
 * Features:
 * - WiFi connection
 * - HTTP API communication
 * - Button control
 * - Display status
 */

#include <M5Core2.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Configuration
const char* WIFI_SSID = "makotaronet";        // あなたのWiFi名
const char* WIFI_PASSWORD = "Makotaro0731Syunpeman0918"; // WiFiパスワード  
const char* API_BASE_URL = "http://192.168.10.7:8000"; // Raspberry Pi のIP

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
    // Initialize M5Stack Core2
    M5.begin();
    M5.Lcd.setTextSize(2);
    M5.Lcd.setTextColor(WHITE, BLACK);
    
    // Display startup message
    M5.Lcd.clear();
    M5.Lcd.setCursor(10, 10);
    M5.Lcd.println("AI Dynamic Painting");
    M5.Lcd.println("Phase 1 - Initializing...");
    
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
    
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        M5.Lcd.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        wifiConnected = true;
        M5.Lcd.println("\nWiFi Connected!");
        M5.Lcd.print("IP: ");
        M5.Lcd.println(WiFi.localIP());
        
        // Display API server info
        M5.Lcd.print("API: ");
        M5.Lcd.println(API_BASE_URL);
    } else {
        M5.Lcd.println("\nWiFi Connection Failed!");
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
    // Button A: Play/Pause
    if (M5.BtnA.wasPressed()) {
        M5.Lcd.fillRect(0, 160, 320, 20, BLACK);
        M5.Lcd.setCursor(10, 160);
        M5.Lcd.setTextColor(YELLOW, BLACK);
        
        if (playbackStatus == "playing") {
            M5.Lcd.println("Sending: Pause");
            sendControlCommand("pause");
        } else {
            M5.Lcd.println("Sending: Play");
            sendControlCommand("play");
        }
    }
    
    // Button B: Stop
    if (M5.BtnB.wasPressed()) {
        M5.Lcd.fillRect(0, 160, 320, 20, BLACK);
        M5.Lcd.setCursor(10, 160);
        M5.Lcd.setTextColor(YELLOW, BLACK);
        M5.Lcd.println("Sending: Stop");
        sendControlCommand("stop");
    }
    
    // Button C: Next Video
    if (M5.BtnC.wasPressed()) {
        M5.Lcd.fillRect(0, 160, 320, 20, BLACK);
        M5.Lcd.setCursor(10, 160);
        M5.Lcd.setTextColor(YELLOW, BLACK);
        M5.Lcd.println("Sending: Next");
        sendControlCommand("next");
    }
}

void checkApiStatus() {
    if (!wifiConnected) {
        return;
    }
    
    HTTPClient http;
    String url = String(API_BASE_URL) + "/api/display/status";
    
    http.begin(url);
    int httpCode = http.GET();
    
    if (httpCode == 200) {
        String payload = http.getString();
        
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
        }
    }
    
    http.end();
}

void sendControlCommand(String command) {
    if (!wifiConnected) {
        M5.Lcd.setCursor(10, 180);
        M5.Lcd.setTextColor(RED, BLACK);
        M5.Lcd.println("Error: No WiFi");
        return;
    }
    
    HTTPClient http;
    String url = String(API_BASE_URL) + "/api/m5stack/control";
    
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    
    // Create JSON payload
    String jsonPayload = "{\"action\":\"" + command + "\"}";
    
    int httpCode = http.POST(jsonPayload);
    
    M5.Lcd.fillRect(0, 180, 320, 20, BLACK);
    M5.Lcd.setCursor(10, 180);
    
    if (httpCode == 200) {
        M5.Lcd.setTextColor(GREEN, BLACK);
        M5.Lcd.println("Command sent successfully");
        
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
    }
    
    http.end();
}