/**
 * AI Dynamic Painting System - Phase 1
 * M5STACK Basic シンプル版
 * 
 * エラー回避版 - 最小限の機能
 */

#include <M5Stack.h>
#include <WiFi.h>

// ===== 設定項目 =====
const char* WIFI_SSID = "makotaronet";
const char* WIFI_PASSWORD = "Makotaro0731Syunpeman0918";
// ===================

void setup() {
    // M5Stack初期化（シンプル版）
    M5.begin();
    
    // シリアル通信開始
    Serial.begin(115200);
    Serial.println("M5Stack Starting...");
    
    // 画面初期化
    M5.Lcd.clear();
    M5.Lcd.setTextSize(2);
    M5.Lcd.setCursor(0, 0);
    M5.Lcd.println("AI Dynamic Painting");
    M5.Lcd.println("Simple Test Mode");
    
    // WiFi接続テスト
    M5.Lcd.println("\nConnecting WiFi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int count = 0;
    while (WiFi.status() != WL_CONNECTED && count < 20) {
        delay(500);
        M5.Lcd.print(".");
        count++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        M5.Lcd.println("\nWiFi Connected!");
        M5.Lcd.print("IP: ");
        M5.Lcd.println(WiFi.localIP());
    } else {
        M5.Lcd.println("\nWiFi Failed!");
    }
    
    // ボタンガイド表示
    M5.Lcd.setCursor(0, 200);
    M5.Lcd.setTextSize(1);
    M5.Lcd.println("A: Test1  B: Test2  C: Test3");
}

void loop() {
    // ボタン状態更新
    M5.update();
    
    // Aボタンテスト
    if (M5.BtnA.wasPressed()) {
        M5.Lcd.fillRect(0, 100, 320, 30, BLACK);
        M5.Lcd.setCursor(0, 100);
        M5.Lcd.setTextSize(2);
        M5.Lcd.println("Button A Pressed!");
        Serial.println("Button A!");
    }
    
    // Bボタンテスト
    if (M5.BtnB.wasPressed()) {
        M5.Lcd.fillRect(0, 100, 320, 30, BLACK);
        M5.Lcd.setCursor(0, 100);
        M5.Lcd.setTextSize(2);
        M5.Lcd.println("Button B Pressed!");
        Serial.println("Button B!");
    }
    
    // Cボタンテスト
    if (M5.BtnC.wasPressed()) {
        M5.Lcd.fillRect(0, 100, 320, 30, BLACK);
        M5.Lcd.setCursor(0, 100);
        M5.Lcd.setTextSize(2);
        M5.Lcd.println("Button C Pressed!");
        Serial.println("Button C!");
    }
    
    delay(100);
}