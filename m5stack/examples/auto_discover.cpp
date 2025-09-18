/**
 * 自動IPアドレス検出機能の例
 * Raspberry Pi を自動で見つける
 */

#include <M5Core2.h>
#include <WiFi.h>
#include <HTTPClient.h>

// 検索するIPアドレス範囲
const char* ip_range = "192.168.10";  // 192.168.10.xxx で検索
const int start_ip = 1;
const int end_ip = 254;
const int api_port = 8000;

String findRaspberryPi() {
    M5.Lcd.println("Raspberry Pi を検索中...");
    
    for (int i = start_ip; i <= end_ip; i++) {
        String test_ip = String(ip_range) + "." + String(i);
        String test_url = "http://" + test_ip + ":" + String(api_port) + "/api/system/health";
        
        M5.Lcd.setCursor(0, 60);
        M5.Lcd.printf("チェック中: %s", test_ip.c_str());
        
        HTTPClient http;
        http.begin(test_url);
        http.setTimeout(1000);  // 1秒タイムアウト
        
        int httpCode = http.GET();
        
        if (httpCode == 200) {
            String response = http.getString();
            if (response.indexOf("api_status") > 0) {  // APIレスポンス確認
                M5.Lcd.setCursor(0, 80);
                M5.Lcd.setTextColor(GREEN);
                M5.Lcd.printf("発見！: %s", test_ip.c_str());
                http.end();
                return test_ip;
            }
        }
        
        http.end();
        delay(100);  // 100ms待機
    }
    
    M5.Lcd.setCursor(0, 80);
    M5.Lcd.setTextColor(RED);
    M5.Lcd.println("Raspberry Pi が見つかりません");
    return "";
}

// 使用例
void setup() {
    M5.begin();
    // WiFi接続後...
    
    String raspberry_ip = findRaspberryPi();
    if (raspberry_ip.length() > 0) {
        String api_base = "http://" + raspberry_ip + ":8000";
        // このapi_baseを使用してAPI通信
    }
}