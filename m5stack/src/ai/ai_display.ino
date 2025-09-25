/**
 * AI Dynamic Painting System - Phase 2
 * M5STACK AI Status Display Enhancements
 * 
 * T268: M5STACK AI status display enhancements implementation
 * Enhanced display system for AI generation status, learning progress, and recommendations
 * 
 * Display Features:
 * - Real-time AI generation status and progress
 * - Learning system analytics and confidence scores
 * - Content recommendations with reasoning
 * - User preference history visualization
 * - System health and connectivity indicators
 */

#include <M5Stack.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <vector>

// ===== Configuration =====
const char* WIFI_SSID = "makotaronet";
const char* WIFI_PASSWORD = "Makotaro0731Syunpeman0918";
const char* API_BASE_URL = "http://192.168.10.7:8000";
const char* DEVICE_ID = "m5stack-display-001";
const char* USER_ID = "m5stack_user_001";

// ===== Display Constants =====
const int SCREEN_WIDTH = 320;
const int SCREEN_HEIGHT = 240;
const int HEADER_HEIGHT = 25;
const int STATUS_HEIGHT = 40;
const int CONTENT_HEIGHT = 150;
const int FOOTER_HEIGHT = 25;

// ===== Global Variables =====
bool wifiConnected = false;
unsigned long lastUpdate = 0;
const unsigned long UPDATE_INTERVAL = 3000;  // Update every 3 seconds
int currentPage = 0;  // 0: Status, 1: Learning, 2: Recommendations
const int MAX_PAGES = 3;

// ===== AI Status Data Structures =====
struct AIGenerationStatus {
    String status = "idle";  // idle, generating, processing, error
    String currentTask = "";
    int progressPercentage = 0;
    String lastGeneration = "";
    int totalGenerated = 0;
    String estimatedCompletion = "";
};

struct LearningProgress {
    int totalInteractions = 0;
    int preferencesLearned = 0;
    float confidenceScore = 0.0;
    bool learningActive = false;
    String lastInteraction = "";
    std::vector<String> recentPreferences;
};

struct Recommendations {
    String nextVideoSuggestion = "";
    float confidence = 0.0;
    String reason = "";
    std::vector<String> alternatives;
    String basedOnContext = "";
};

struct SystemStatus {
    bool aiEnabled = false;
    String learningMode = "active";
    String lastSync = "";
    bool apiConnected = false;
    String connectionQuality = "unknown";
};

// Global status objects
AIGenerationStatus genStatus;
LearningProgress learning;
Recommendations recommendations;
SystemStatus systemStatus;

// ===== Function Declarations =====
void setupWiFi();
void setupDisplay();
void updateAIData();
void displayCurrentPage();
void displayStatusPage();
void displayLearningPage();
void displayRecommendationsPage();
void displayHeader();
void displayFooter();
void handleButtons();
void drawProgressBar(int x, int y, int width, int height, int progress, uint16_t color);
void drawStatusIndicator(int x, int y, bool status, String label);
String formatTime(String timestamp);
String truncateString(String str, int maxLength);

void setup() {
    // Initialize M5Stack
    M5.begin(true, false, true);
    M5.Power.begin();
    
    Serial.begin(115200);
    Serial.println("=== AI Dynamic Painting M5STACK AI Display ===");
    
    // Setup display
    setupDisplay();
    
    // Setup WiFi
    setupWiFi();
    
    // Initial data update
    updateAIData();
    
    Serial.println("AI Display initialized successfully");
}

void loop() {
    M5.update();
    
    // Handle button navigation
    handleButtons();
    
    // Update AI data periodically
    if (millis() - lastUpdate > UPDATE_INTERVAL) {
        updateAIData();
        lastUpdate = millis();
    }
    
    // Display current page
    displayCurrentPage();
    
    delay(100);
}

void setupWiFi() {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setTextSize(2);
    M5.Lcd.setCursor(10, 10);
    M5.Lcd.println("AI Display Setup");
    
    M5.Lcd.setTextSize(1);
    M5.Lcd.setCursor(10, 40);
    M5.Lcd.println("Connecting to WiFi...");
    
    Serial.print("Connecting to ");
    Serial.println(WIFI_SSID);
    
    // Connect to specific router
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
        systemStatus.apiConnected = true;
        systemStatus.connectionQuality = "good";
        
        M5.Lcd.println();
        M5.Lcd.setTextColor(GREEN, BLACK);
        M5.Lcd.println("WiFi Connected!");
        M5.Lcd.setTextColor(WHITE, BLACK);
        M5.Lcd.print("IP: ");
        M5.Lcd.println(WiFi.localIP());
        
        Serial.println();
        Serial.println("WiFi Connected!");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
    } else {
        wifiConnected = false;
        systemStatus.apiConnected = false;
        systemStatus.connectionQuality = "failed";
        
        M5.Lcd.println();
        M5.Lcd.setTextColor(RED, BLACK);
        M5.Lcd.println("WiFi Connection Failed!");
        
        Serial.println();
        Serial.println("WiFi Connection Failed!");
    }
    
    delay(2000);
}

void setupDisplay() {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setRotation(1);  // Landscape orientation
    M5.Lcd.setTextColor(WHITE, BLACK);
    
    // Display initial message
    M5.Lcd.setTextSize(2);
    M5.Lcd.setCursor(50, 100);
    M5.Lcd.println("AI Display Initializing...");
    
    delay(1000);
}

void updateAIData() {
    if (!wifiConnected) {
        systemStatus.apiConnected = false;
        return;
    }
    
    HTTPClient http;
    String url = String(API_BASE_URL) + "/api/m5stack/ai-status";
    
    Serial.print("Updating AI data from: ");
    Serial.println(url);
    
    http.begin(url);
    int httpCode = http.GET();
    
    if (httpCode == 200) {
        String payload = http.getString();
        Serial.print("AI Status Response: ");
        Serial.println(payload);
        
        DynamicJsonDocument doc(4096);
        DeserializationError error = deserializeJson(doc, payload);
        
        if (!error) {
            systemStatus.apiConnected = true;
            systemStatus.lastSync = "Now";
            
            // Update generation status
            JsonObject genStatusJson = doc["ai_generation_status"];
            if (genStatusJson) {
                genStatus.status = genStatusJson["status"].as<String>();
                genStatus.currentTask = genStatusJson["current_task"] | "";
                genStatus.progressPercentage = genStatusJson["progress_percentage"] | 0;
                genStatus.lastGeneration = genStatusJson["last_generation"] | "";
                genStatus.totalGenerated = genStatusJson["total_generated"] | 0;
            }
            
            // Update learning progress
            JsonObject learningJson = doc["learning_progress"];
            if (learningJson) {
                learning.totalInteractions = learningJson["total_interactions"] | 0;
                learning.preferencesLearned = learningJson["preferences_learned"] | 0;
                learning.confidenceScore = learningJson["confidence_score"] | 0.0;
                learning.learningActive = learningJson["learning_active"] | false;
            }
            
            // Update recommendations
            JsonObject recJson = doc["current_recommendations"];
            if (recJson) {
                recommendations.nextVideoSuggestion = recJson["next_video_suggestion"] | "";
                recommendations.confidence = recJson["confidence"] | 0.0;
                recommendations.reason = recJson["reason"] | "";
            }
            
            // Update device status
            JsonObject deviceJson = doc["device_status"];
            if (deviceJson) {
                systemStatus.aiEnabled = deviceJson["ai_features_enabled"] | false;
                systemStatus.learningMode = deviceJson["learning_mode"] | "unknown";
            }
            
            Serial.println("AI data updated successfully");
        } else {
            Serial.print("JSON Parse Error: ");
            Serial.println(error.c_str());
            systemStatus.apiConnected = false;
        }
    } else {
        Serial.print("HTTP Error: ");
        Serial.println(httpCode);
        systemStatus.apiConnected = false;
        systemStatus.connectionQuality = "poor";
    }
    
    http.end();
}

void displayCurrentPage() {
    static int lastPage = -1;
    static unsigned long lastDisplayUpdate = 0;
    
    // Only redraw if page changed or enough time passed
    if (currentPage != lastPage || millis() - lastDisplayUpdate > 1000) {
        M5.Lcd.fillScreen(BLACK);
        
        displayHeader();
        
        switch (currentPage) {
            case 0:
                displayStatusPage();
                break;
            case 1:
                displayLearningPage();
                break;
            case 2:
                displayRecommendationsPage();
                break;
        }
        
        displayFooter();
        
        lastPage = currentPage;
        lastDisplayUpdate = millis();
    }
}

void displayHeader() {
    // Header background
    M5.Lcd.fillRect(0, 0, SCREEN_WIDTH, HEADER_HEIGHT, BLUE);
    
    // Title and connection status
    M5.Lcd.setTextSize(1);
    M5.Lcd.setTextColor(WHITE, BLUE);
    M5.Lcd.setCursor(5, 8);
    M5.Lcd.print("AI Dynamic Painting");
    
    // Connection indicator
    M5.Lcd.setCursor(200, 8);
    if (systemStatus.apiConnected) {
        M5.Lcd.setTextColor(GREEN, BLUE);
        M5.Lcd.print("ONLINE");
    } else {
        M5.Lcd.setTextColor(RED, BLUE);
        M5.Lcd.print("OFFLINE");
    }
    
    // Page indicator
    M5.Lcd.setCursor(270, 8);
    M5.Lcd.setTextColor(WHITE, BLUE);
    M5.Lcd.print(String(currentPage + 1) + "/" + String(MAX_PAGES));
}

void displayStatusPage() {
    int yPos = HEADER_HEIGHT + 10;
    
    // Page title
    M5.Lcd.setTextSize(2);
    M5.Lcd.setTextColor(CYAN, BLACK);
    M5.Lcd.setCursor(10, yPos);
    M5.Lcd.println("AI STATUS");
    yPos += 25;
    
    // Generation status
    M5.Lcd.setTextSize(1);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setCursor(10, yPos);
    M5.Lcd.print("Generation: ");
    
    if (genStatus.status == "generating") {
        M5.Lcd.setTextColor(GREEN, BLACK);
        M5.Lcd.println("ACTIVE");
        yPos += 15;
        
        // Progress bar
        M5.Lcd.setCursor(10, yPos);
        M5.Lcd.setTextColor(WHITE, BLACK);
        M5.Lcd.print("Progress: " + String(genStatus.progressPercentage) + "%");
        yPos += 15;
        drawProgressBar(10, yPos, 200, 10, genStatus.progressPercentage, GREEN);
        yPos += 20;
        
        // Current task
        if (!genStatus.currentTask.isEmpty()) {
            M5.Lcd.setCursor(10, yPos);
            M5.Lcd.println("Task: " + truncateString(genStatus.currentTask, 30));
            yPos += 15;
        }
    } else {
        if (genStatus.status == "idle") {
            M5.Lcd.setTextColor(YELLOW, BLACK);
            M5.Lcd.println("IDLE");
        } else if (genStatus.status == "error") {
            M5.Lcd.setTextColor(RED, BLACK);
            M5.Lcd.println("ERROR");
        } else {
            M5.Lcd.setTextColor(WHITE, BLACK);
            String upperStatus = genStatus.status;
            upperStatus.toUpperCase();
            M5.Lcd.println(upperStatus);
        }
        yPos += 20;
    }
    
    // Total generated
    M5.Lcd.setCursor(10, yPos);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.println("Total Generated: " + String(genStatus.totalGenerated));
    yPos += 15;
    
    // Last generation time
    if (!genStatus.lastGeneration.isEmpty()) {
        M5.Lcd.setCursor(10, yPos);
        M5.Lcd.println("Last: " + formatTime(genStatus.lastGeneration));
        yPos += 15;
    }
    
    // System status indicators
    yPos += 10;
    drawStatusIndicator(10, yPos, systemStatus.aiEnabled, "AI");
    drawStatusIndicator(80, yPos, learning.learningActive, "Learning");
    drawStatusIndicator(150, yPos, systemStatus.apiConnected, "API");
}

void displayLearningPage() {
    int yPos = HEADER_HEIGHT + 10;
    
    // Page title
    M5.Lcd.setTextSize(2);
    M5.Lcd.setTextColor(MAGENTA, BLACK);
    M5.Lcd.setCursor(10, yPos);
    M5.Lcd.println("LEARNING");
    yPos += 25;
    
    // Learning statistics
    M5.Lcd.setTextSize(1);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setCursor(10, yPos);
    M5.Lcd.println("Interactions: " + String(learning.totalInteractions));
    yPos += 15;
    
    M5.Lcd.setCursor(10, yPos);
    M5.Lcd.println("Preferences: " + String(learning.preferencesLearned));
    yPos += 15;
    
    // Confidence score
    M5.Lcd.setCursor(10, yPos);
    M5.Lcd.print("Confidence: " + String(learning.confidenceScore * 100, 1) + "%");
    yPos += 15;
    
    // Confidence bar
    int confidencePercent = (int)(learning.confidenceScore * 100);
    drawProgressBar(10, yPos, 200, 10, confidencePercent, CYAN);
    yPos += 20;
    
    // Learning mode
    M5.Lcd.setCursor(10, yPos);
    M5.Lcd.print("Mode: ");
    if (learning.learningActive) {
        M5.Lcd.setTextColor(GREEN, BLACK);
        M5.Lcd.println("ACTIVE");
    } else {
        M5.Lcd.setTextColor(YELLOW, BLACK);
        M5.Lcd.println("PAUSED");
    }
    yPos += 20;
    
    // Recent interactions visualization
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setCursor(10, yPos);
    M5.Lcd.println("Recent Feedback:");
    yPos += 15;
    
    // Display simple feedback indicators (if we had historical data)
    for (int i = 0; i < 10; i++) {
        int x = 20 + (i * 25);
        int y = yPos;
        
        // Mock recent feedback visualization
        uint16_t color = (i % 3 == 0) ? GREEN : (i % 3 == 1) ? RED : YELLOW;
        M5.Lcd.fillCircle(x, y, 6, color);
    }
    yPos += 20;
    
    // Legend
    M5.Lcd.setTextSize(1);
    M5.Lcd.setCursor(10, yPos);
    M5.Lcd.setTextColor(GREEN, BLACK);
    M5.Lcd.print("●Good ");
    M5.Lcd.setTextColor(RED, BLACK);
    M5.Lcd.print("●Bad ");
    M5.Lcd.setTextColor(YELLOW, BLACK);
    M5.Lcd.print("●Skip");
}

void displayRecommendationsPage() {
    int yPos = HEADER_HEIGHT + 10;
    
    // Page title
    M5.Lcd.setTextSize(2);
    M5.Lcd.setTextColor(ORANGE, BLACK);
    M5.Lcd.setCursor(10, yPos);
    M5.Lcd.println("RECOMMEND");
    yPos += 25;
    
    // Next recommendation
    M5.Lcd.setTextSize(1);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setCursor(10, yPos);
    M5.Lcd.println("Next Video:");
    yPos += 15;
    
    if (!recommendations.nextVideoSuggestion.isEmpty()) {
        M5.Lcd.setCursor(10, yPos);
        M5.Lcd.setTextColor(CYAN, BLACK);
        M5.Lcd.println(truncateString(recommendations.nextVideoSuggestion, 35));
        yPos += 15;
        
        // Confidence
        M5.Lcd.setCursor(10, yPos);
        M5.Lcd.setTextColor(WHITE, BLACK);
        M5.Lcd.print("Confidence: " + String(recommendations.confidence * 100, 1) + "%");
        yPos += 15;
        
        // Confidence bar
        int confPercent = (int)(recommendations.confidence * 100);
        drawProgressBar(10, yPos, 150, 8, confPercent, ORANGE);
        yPos += 20;
        
        // Reason
        if (!recommendations.reason.isEmpty()) {
            M5.Lcd.setCursor(10, yPos);
            M5.Lcd.setTextColor(YELLOW, BLACK);
            M5.Lcd.println("Reason:");
            yPos += 12;
            
            M5.Lcd.setCursor(10, yPos);
            M5.Lcd.setTextColor(WHITE, BLACK);
            M5.Lcd.println(truncateString(recommendations.reason, 40));
            yPos += 15;
        }
    } else {
        M5.Lcd.setCursor(10, yPos);
        M5.Lcd.setTextColor(YELLOW, BLACK);
        M5.Lcd.println("No recommendation available");
        yPos += 15;
        
        M5.Lcd.setCursor(10, yPos);
        M5.Lcd.setTextColor(WHITE, BLACK);
        M5.Lcd.println("Learning more about your");
        yPos += 12;
        M5.Lcd.setCursor(10, yPos);
        M5.Lcd.println("preferences...");
        yPos += 20;
    }
    
    // Alternative suggestions (if available)
    if (recommendations.alternatives.size() > 0) {
        M5.Lcd.setCursor(10, yPos);
        M5.Lcd.setTextColor(WHITE, BLACK);
        M5.Lcd.println("Alternatives:");
        yPos += 15;
        
        for (int i = 0; i < min((int)recommendations.alternatives.size(), 2); i++) {
            M5.Lcd.setCursor(15, yPos);
            M5.Lcd.setTextColor(CYAN, BLACK);
            M5.Lcd.println("• " + truncateString(recommendations.alternatives[i], 30));
            yPos += 12;
        }
    }
}

void displayFooter() {
    int yPos = SCREEN_HEIGHT - FOOTER_HEIGHT;
    
    // Footer background
    M5.Lcd.fillRect(0, yPos, SCREEN_WIDTH, FOOTER_HEIGHT, DARKGREY);
    
    // Button labels
    M5.Lcd.setTextSize(1);
    M5.Lcd.setTextColor(WHITE, DARKGREY);
    M5.Lcd.setCursor(5, yPos + 8);
    M5.Lcd.print("A:Prev");
    
    M5.Lcd.setCursor(140, yPos + 8);
    M5.Lcd.print("B:Refresh");
    
    M5.Lcd.setCursor(250, yPos + 8);
    M5.Lcd.print("C:Next");
}

void handleButtons() {
    // Button A: Previous page
    if (M5.BtnA.wasReleased()) {
        currentPage = (currentPage - 1 + MAX_PAGES) % MAX_PAGES;
        Serial.println("Switched to page: " + String(currentPage));
    }
    
    // Button B: Refresh data
    if (M5.BtnB.wasReleased()) {
        M5.Lcd.fillRect(0, HEADER_HEIGHT, SCREEN_WIDTH, 20, BLACK);
        M5.Lcd.setTextColor(YELLOW, BLACK);
        M5.Lcd.setCursor(10, HEADER_HEIGHT + 5);
        M5.Lcd.println("Refreshing...");
        
        updateAIData();
        Serial.println("Manual data refresh triggered");
    }
    
    // Button C: Next page
    if (M5.BtnC.wasReleased()) {
        currentPage = (currentPage + 1) % MAX_PAGES;
        Serial.println("Switched to page: " + String(currentPage));
    }
}

void drawProgressBar(int x, int y, int width, int height, int progress, uint16_t color) {
    // Border
    M5.Lcd.drawRect(x, y, width, height, WHITE);
    
    // Background
    M5.Lcd.fillRect(x + 1, y + 1, width - 2, height - 2, BLACK);
    
    // Progress fill
    int fillWidth = ((width - 2) * progress) / 100;
    if (fillWidth > 0) {
        M5.Lcd.fillRect(x + 1, y + 1, fillWidth, height - 2, color);
    }
}

void drawStatusIndicator(int x, int y, bool status, String label) {
    // Circle indicator
    uint16_t color = status ? GREEN : RED;
    M5.Lcd.fillCircle(x + 8, y + 8, 6, color);
    M5.Lcd.drawCircle(x + 8, y + 8, 7, WHITE);
    
    // Label
    M5.Lcd.setTextSize(1);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setCursor(x, y + 18);
    M5.Lcd.println(label);
}

String formatTime(String timestamp) {
    // Simple time formatting (could be enhanced)
    if (timestamp.length() > 10) {
        return timestamp.substring(11, 16);  // Extract HH:MM
    }
    return timestamp;
}

String truncateString(String str, int maxLength) {
    if (str.length() <= maxLength) {
        return str;
    }
    return str.substring(0, maxLength - 3) + "...";
}