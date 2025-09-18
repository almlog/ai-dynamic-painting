/**
 * AI Dynamic Painting System - Phase 2
 * M5STACK AI Preference Controls (Enhanced with AI Features)
 * 
 * T267: M5STACK AI preference buttons implementation
 * Enhanced version of basic controls with AI preference learning
 * 
 * Button Mapping (AI Mode):
 * - A: Good (Like) - AI preference: positive feedback
 * - B: Bad (Dislike) - AI preference: negative feedback  
 * - C: Skip - AI preference: neutral/skip feedback
 * 
 * Long Press (>1 second):
 * - A: Switch to Play/Pause mode
 * - B: Switch to Stop mode
 * - C: Switch to Next mode
 */

#include <M5Stack.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>

// ===== Configuration =====
const char* WIFI_SSID = "makotaronet";
const char* WIFI_PASSWORD = "Makotaro0731Syunpeman0918";
const char* API_BASE_URL = "http://192.168.10.7:8000";
const char* DEVICE_ID = "m5stack-ai-001";
const char* USER_ID = "m5stack_user_001";

// ===== Global Variables =====
bool wifiConnected = false;
String currentVideoId = "";
String playbackStatus = "idle";
String aiMode = "preference";  // "preference" or "control"
unsigned long lastApiCheck = 0;
const unsigned long API_CHECK_INTERVAL = 5000;
unsigned long buttonPressStart = 0;
const unsigned long LONG_PRESS_DURATION = 1000;

// AI Status Data
struct AIStatus {
  String generationStatus = "idle";
  int progressPercentage = 0;
  float confidenceScore = 0.0;
  String nextRecommendation = "";
  bool learningActive = false;
  int totalInteractions = 0;
};

AIStatus aiStatus;
Preferences preferences;

// ===== Function Declarations =====
void setupWiFi();
void setupPreferences();
void updateDisplay();
void handleButtons();
void handleAIPreferenceButtons();
void handleControlButtons();
void checkApiStatus();
void sendControlCommand(String command);
void sendAIPreference(String preference, String reason = "");
void updateAIStatus();
void displayAIMode();
void displayControlMode();
void switchMode();

void setup() {
    // Initialize M5Stack
    M5.begin(true, false, true);
    M5.Power.begin();
    
    M5.Lcd.setTextSize(2);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.clear();
    
    Serial.begin(115200);
    Serial.println("=== AI Dynamic Painting M5STACK AI Controls ===");
    
    // Setup preferences for persistent storage
    setupPreferences();
    
    // Display startup message
    M5.Lcd.setCursor(10, 10);
    M5.Lcd.println("AI Dynamic Painting");
    M5.Lcd.println("Phase 2 - AI Enhanced");
    M5.Lcd.println("Initializing...");
    
    // Setup WiFi
    setupWiFi();
    
    // Load AI mode from preferences
    aiMode = preferences.getString("ai_mode", "preference");
    
    // Initial display setup
    displayAIMode();
    
    // Get initial AI status
    updateAIStatus();
}

void loop() {
    M5.update();
    
    // Handle buttons based on current mode
    if (aiMode == "preference") {
        handleAIPreferenceButtons();
    } else {
        handleControlButtons();
    }
    
    // Check API status periodically
    if (millis() - lastApiCheck > API_CHECK_INTERVAL) {
        checkApiStatus();
        updateAIStatus();
        lastApiCheck = millis();
    }
    
    // Update display
    updateDisplay();
    
    delay(100);
}

void setupWiFi() {
    M5.Lcd.setCursor(10, 50);
    M5.Lcd.println("Connecting to WiFi...");
    Serial.print("Connecting to ");
    Serial.println(WIFI_SSID);
    
    // Connect to specific router (same as Phase 1)
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
        M5.Lcd.println("\\nWiFi Connected!");
        M5.Lcd.print("IP: ");
        M5.Lcd.println(WiFi.localIP());
        Serial.println("\\nWiFi Connected!");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
    } else {
        M5.Lcd.println("\\nWiFi Connection Failed!");
        Serial.println("\\nWiFi Connection Failed!");
        wifiConnected = false;
    }
    
    delay(2000);
}

void setupPreferences() {
    preferences.begin("ai-controls", false);
    Serial.println("Preferences initialized");
}

void updateDisplay() {
    static unsigned long lastUpdate = 0;
    
    if (millis() - lastUpdate < 1000) {
        return;
    }
    lastUpdate = millis();
    
    // Clear main display area
    M5.Lcd.fillRect(0, 70, 320, 120, BLACK);
    
    // Display mode-specific content
    if (aiMode == "preference") {
        displayAIMode();
    } else {
        displayControlMode();
    }
}

void handleAIPreferenceButtons() {
    // Button A: Good (Like)
    if (M5.BtnA.wasPressed()) {
        buttonPressStart = millis();
    }
    if (M5.BtnA.wasReleased()) {
        unsigned long pressDuration = millis() - buttonPressStart;
        if (pressDuration > LONG_PRESS_DURATION) {
            // Long press: switch to control mode
            aiMode = "control";
            preferences.putString("ai_mode", aiMode);
            M5.Lcd.fillScreen(BLACK);
            M5.Lcd.setCursor(10, 100);
            M5.Lcd.setTextColor(GREEN, BLACK);
            M5.Lcd.println("Switched to Control Mode");
            delay(1000);
        } else {
            // Short press: send good preference
            sendAIPreference("good", "User liked current content");
            M5.Lcd.fillRect(0, 160, 320, 20, BLACK);
            M5.Lcd.setCursor(10, 160);
            M5.Lcd.setTextColor(GREEN, BLACK);
            M5.Lcd.println("Good! AI Learning...");
        }
    }
    
    // Button B: Bad (Dislike)
    if (M5.BtnB.wasPressed()) {
        buttonPressStart = millis();
    }
    if (M5.BtnB.wasReleased()) {
        unsigned long pressDuration = millis() - buttonPressStart;
        if (pressDuration > LONG_PRESS_DURATION) {
            // Long press: switch to control mode
            aiMode = "control";
            preferences.putString("ai_mode", aiMode);
            M5.Lcd.fillScreen(BLACK);
            M5.Lcd.setCursor(10, 100);
            M5.Lcd.setTextColor(YELLOW, BLACK);
            M5.Lcd.println("Switched to Control Mode");
            delay(1000);
        } else {
            // Short press: send bad preference
            sendAIPreference("bad", "User disliked current content");
            M5.Lcd.fillRect(0, 160, 320, 20, BLACK);
            M5.Lcd.setCursor(10, 160);
            M5.Lcd.setTextColor(RED, BLACK);
            M5.Lcd.println("Bad! AI Learning...");
        }
    }
    
    // Button C: Skip
    if (M5.BtnC.wasPressed()) {
        buttonPressStart = millis();
    }
    if (M5.BtnC.wasReleased()) {
        unsigned long pressDuration = millis() - buttonPressStart;
        if (pressDuration > LONG_PRESS_DURATION) {
            // Long press: switch to control mode
            aiMode = "control";
            preferences.putString("ai_mode", aiMode);
            M5.Lcd.fillScreen(BLACK);
            M5.Lcd.setCursor(10, 100);
            M5.Lcd.setTextColor(CYAN, BLACK);
            M5.Lcd.println("Switched to Control Mode");
            delay(1000);
        } else {
            // Short press: send skip preference
            sendAIPreference("skip", "User skipped current content");
            M5.Lcd.fillRect(0, 160, 320, 20, BLACK);
            M5.Lcd.setCursor(10, 160);
            M5.Lcd.setTextColor(YELLOW, BLACK);
            M5.Lcd.println("Skip! AI Learning...");
        }
    }
}

void handleControlButtons() {
    // Standard control mode (same as Phase 1)
    if (M5.BtnA.wasPressed()) {
        buttonPressStart = millis();
    }
    if (M5.BtnA.wasReleased()) {
        unsigned long pressDuration = millis() - buttonPressStart;
        if (pressDuration > LONG_PRESS_DURATION) {
            // Long press: switch to AI preference mode
            switchMode();
        } else {
            // Short press: play/pause
            sendControlCommand("play_pause");
        }
    }
    
    if (M5.BtnB.wasReleased()) {
        sendControlCommand("stop");
    }
    
    if (M5.BtnC.wasReleased()) {
        sendControlCommand("next");
    }
}

void sendAIPreference(String preference, String reason) {
    if (!wifiConnected) {
        Serial.println("Error: No WiFi connection for AI preference");
        return;
    }
    
    HTTPClient http;
    String url = String(API_BASE_URL) + "/api/m5stack/ai-preference";
    
    Serial.print("Sending AI preference to: ");
    Serial.println(url);
    
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    
    // Create JSON payload for AI preference
    DynamicJsonDocument doc(1024);
    doc["user_id"] = USER_ID;
    doc["action"] = "ai_preference";
    doc["preference_type"] = preference;
    doc["content_id"] = currentVideoId.isEmpty() ? "unknown" : currentVideoId;
    
    JsonObject deviceInfo = doc.createNestedObject("device_info");
    deviceInfo["device_id"] = DEVICE_ID;
    deviceInfo["button_pressed"] = preference;
    deviceInfo["timestamp"] = "2025-09-18T" + String(millis() / 1000) + "Z";
    deviceInfo["reason"] = reason;
    
    String jsonPayload;
    serializeJson(doc, jsonPayload);
    
    Serial.print("AI Preference Payload: ");
    Serial.println(jsonPayload);
    
    int httpCode = http.POST(jsonPayload);
    
    if (httpCode == 200) {
        String response = http.getString();
        Serial.println("AI Preference sent successfully");
        Serial.print("Response: ");
        Serial.println(response);
        
        // Parse response to update AI status
        DynamicJsonDocument responseDoc(1024);
        DeserializationError error = deserializeJson(responseDoc, response);
        if (!error) {
            aiStatus.totalInteractions++;
            preferences.putInt("total_interactions", aiStatus.totalInteractions);
        }
    } else {
        Serial.print("AI Preference Error: HTTP ");
        Serial.println(httpCode);
    }
    
    http.end();
}

void sendControlCommand(String command) {
    if (!wifiConnected) {
        Serial.println("Error: No WiFi connection for control command");
        return;
    }
    
    HTTPClient http;
    String url = String(API_BASE_URL) + "/api/m5stack/control";
    
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    
    String jsonPayload = "{\\"action\\":\\"" + command + "\\",\\"device_info\\":{\\"device_id\\":\\"" + DEVICE_ID + "\\"}}";
    
    int httpCode = http.POST(jsonPayload);
    
    if (httpCode == 200) {
        Serial.println("Control command sent successfully");
    } else {
        Serial.print("Control Error: HTTP ");
        Serial.println(httpCode);
    }
    
    http.end();
}

void checkApiStatus() {
    if (!wifiConnected) return;
    
    HTTPClient http;
    String url = String(API_BASE_URL) + "/api/display/status";
    
    http.begin(url);
    int httpCode = http.GET();
    
    if (httpCode == 200) {
        String payload = http.getString();
        
        DynamicJsonDocument doc(1024);
        DeserializationError error = deserializeJson(doc, payload);
        
        if (!error) {
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

void updateAIStatus() {
    if (!wifiConnected) return;
    
    HTTPClient http;
    String url = String(API_BASE_URL) + "/api/m5stack/ai-status";
    
    http.begin(url);
    int httpCode = http.GET();
    
    if (httpCode == 200) {
        String payload = http.getString();
        
        DynamicJsonDocument doc(2048);
        DeserializationError error = deserializeJson(doc, payload);
        
        if (!error) {
            // Update AI status from API response
            JsonObject genStatus = doc["ai_generation_status"];
            if (genStatus) {
                aiStatus.generationStatus = genStatus["status"].as<String>();
                aiStatus.progressPercentage = genStatus["progress_percentage"].as<int>();
            }
            
            JsonObject learningProgress = doc["learning_progress"];
            if (learningProgress) {
                aiStatus.totalInteractions = learningProgress["total_interactions"].as<int>();
                aiStatus.confidenceScore = learningProgress["confidence_score"].as<float>();
                aiStatus.learningActive = learningProgress["learning_active"].as<bool>();
            }
            
            JsonObject recommendations = doc["current_recommendations"];
            if (recommendations) {
                aiStatus.nextRecommendation = recommendations["next_video_suggestion"].as<String>();
            }
        }
    }
    
    http.end();
}

void displayAIMode() {
    // Display AI mode information
    M5.Lcd.setCursor(10, 70);
    M5.Lcd.setTextSize(2);
    M5.Lcd.setTextColor(CYAN, BLACK);
    M5.Lcd.println("AI PREFERENCE MODE");
    
    // Display AI status
    M5.Lcd.setCursor(10, 95);
    M5.Lcd.setTextSize(1);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.print("AI Status: ");
    if (aiStatus.generationStatus == "generating") {
        M5.Lcd.setTextColor(GREEN, BLACK);
        M5.Lcd.println("Generating (" + String(aiStatus.progressPercentage) + "%)");
    } else {
        M5.Lcd.setTextColor(YELLOW, BLACK);
        M5.Lcd.println(aiStatus.generationStatus);
    }
    
    // Display learning progress
    M5.Lcd.setCursor(10, 110);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.print("Learning: ");
    M5.Lcd.print(String(aiStatus.totalInteractions));
    M5.Lcd.print(" interactions, ");
    M5.Lcd.print(String(aiStatus.confidenceScore * 100, 1));
    M5.Lcd.println("% confidence");
    
    // Display current video
    if (!currentVideoId.isEmpty()) {
        M5.Lcd.setCursor(10, 125);
        M5.Lcd.print("Video: ");
        M5.Lcd.println(currentVideoId.substring(0, 20));  // Truncate for display
    }
    
    // Display next recommendation
    if (!aiStatus.nextRecommendation.isEmpty()) {
        M5.Lcd.setCursor(10, 140);
        M5.Lcd.setTextColor(CYAN, BLACK);
        M5.Lcd.print("Next: ");
        M5.Lcd.println(aiStatus.nextRecommendation.substring(0, 15));
    }
    
    // Button labels
    M5.Lcd.setCursor(10, 200);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.println("A:Good  B:Bad  C:Skip");
    M5.Lcd.setCursor(10, 215);
    M5.Lcd.setTextSize(1);
    M5.Lcd.println("(Long press to switch mode)");
}

void displayControlMode() {
    // Display standard control mode
    M5.Lcd.setCursor(10, 70);
    M5.Lcd.setTextSize(2);
    M5.Lcd.setTextColor(YELLOW, BLACK);
    M5.Lcd.println("CONTROL MODE");
    
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
    
    // Display current video
    if (!currentVideoId.isEmpty()) {
        M5.Lcd.setCursor(10, 130);
        M5.Lcd.setTextSize(1);
        M5.Lcd.setTextColor(WHITE, BLACK);
        M5.Lcd.print("Video: ");
        M5.Lcd.println(currentVideoId);
    }
    
    // Button labels
    M5.Lcd.setCursor(10, 200);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.println("A:Play/Pause  B:Stop  C:Next");
    M5.Lcd.setCursor(10, 215);
    M5.Lcd.setTextSize(1);
    M5.Lcd.println("(Long press A to switch mode)");
}

void switchMode() {
    aiMode = "preference";
    preferences.putString("ai_mode", aiMode);
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setCursor(10, 100);
    M5.Lcd.setTextColor(CYAN, BLACK);
    M5.Lcd.println("Switched to AI Mode");
    delay(1000);
}