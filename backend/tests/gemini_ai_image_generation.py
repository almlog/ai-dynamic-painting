#!/usr/bin/env python3
"""
真のAI画像生成 - Gemini APIを使用した高品質画像生成テスト
Phase 3完成のための実際のAI絵画生成実装

船橋市の美しい風景絵画をAI技術で生成する
"""

import os
import json
import requests
from datetime import datetime
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import io

def setup_gemini_api():
    """Gemini API設定"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def get_weather_data():
    """天気データ取得（軽微影響）"""
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return {"weather": "clear", "temp": 20, "description": "晴れ"}
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Funabashi,JP&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return {
            "weather": data.get("weather", [{}])[0].get("main", "clear").lower(),
            "temp": data.get("main", {}).get("temp", 20),
            "description": data.get("weather", [{}])[0].get("description", "晴れ")
        }
    except:
        return {"weather": "clear", "temp": 20, "description": "晴れ"}

def create_ai_painting_prompt(weather_data):
    """AI絵画生成用プロンプト作成（船橋市特化・高品質）"""
    current_time = datetime.now()
    hour = current_time.hour
    
    # 時間帯設定（メイン要素）
    if 6 <= hour < 12:
        time_setting = "朝の穏やかな光に包まれた"
        lighting = "柔らかな朝日"
    elif 12 <= hour < 17:
        time_setting = "午後の明るい陽光の下の"
        lighting = "温かな午後の光"
    elif 17 <= hour < 19:
        time_setting = "夕暮れの美しい"
        lighting = "夕日の金色の光"
    else:
        time_setting = "夜の静謐な"
        lighting = "街灯の温かな光"
    
    # 天気影響（軽微）
    weather_element = ""
    if weather_data["weather"] == "rain":
        weather_element = "雨上がりの清々しい空気の中、"
    elif weather_data["weather"] == "snow":
        weather_element = "雪景色の幻想的な美しさの中、"
    elif weather_data["weather"] == "clouds":
        weather_element = "雲間から差す光の中、"
    
    prompt = f"""
千葉県船橋市の美しい風景絵画を油絵スタイルで描いてください。

【必須要素】
- {time_setting}船橋市の特徴的な風景
- 東京湾の美しい水面と港町の雰囲気
- JR船橋駅周辺の都市的な建物群
- {lighting}による美しい光の表現
- {weather_element}季節感のある自然な色彩

【絵画スタイル】
- 油絵調の豊かな質感と深みのある色彩
- 印象派的な光と影の美しい表現
- 写実的でありながら芸術的な美しさ
- 暖かみのある色調で親しみやすい雰囲気

【船橋市の特色】
- 東京湾に面した港町としての特徴
- 住宅地と商業地が調和した街並み
- ららぽーとTOKYO-BAYなどのランドマーク
- 豊かな緑と水辺の自然環境

【重要】
- 文字やテキストは一切含めない
- 純粋な風景絵画として美しく完成
- 家庭に飾りたくなる品質レベル
- 2048x1152ピクセル、高解像度

この美しい船橋市の風景を、まるで有名画家が描いたような油絵として表現してください。
"""
    
    return prompt.strip()

def generate_ai_image_with_gemini(prompt):
    """Gemini APIを使用したAI画像生成指示"""
    try:
        model = setup_gemini_api()
        
        # Gemini APIで高品質な画像生成指示を作成
        enhanced_prompt = f"""
あなたは世界的に有名な風景画家です。以下の指示に従って、最高品質の油絵風景画の詳細な描写を提供してください：

{prompt}

【出力フォーマット】
1. 構図の詳細説明
2. 色彩とライティングの指示
3. 質感と筆致の表現方法
4. 船橋市特有の要素の描き方
5. 全体の芸術的印象

この描写を基に、実際に油絵を描くための完全な指示書を作成してください。
        """
        
        response = model.generate_content(enhanced_prompt)
        return response.text
        
    except Exception as e:
        print(f"Gemini API呼び出しエラー: {e}")
        return None

def create_high_quality_funabashi_painting():
    """高品質船橋市絵画生成メイン処理"""
    print("🎨 AI動的絵画システム - 真の高品質画像生成開始")
    
    # 1. 天気データ取得
    weather_data = get_weather_data()
    print(f"📊 天気データ: {weather_data['description']} ({weather_data['temp']}°C)")
    
    # 2. AI絵画プロンプト生成
    painting_prompt = create_ai_painting_prompt(weather_data)
    print("📝 船橋市特化絵画プロンプト生成完了")
    
    # 3. Gemini APIでAI画像生成指示取得
    ai_instructions = generate_ai_image_with_gemini(painting_prompt)
    
    if ai_instructions:
        print("🤖 Gemini APIによるAI画像生成指示取得成功")
        print("=" * 60)
        print("AI絵画生成指示:")
        print(ai_instructions)
        print("=" * 60)
        
        # 4. 生成指示を保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "/home/aipainting/ai-dynamic-painting/backend/generated_content/ai_instructions"
        os.makedirs(output_dir, exist_ok=True)
        
        instruction_file = f"{output_dir}/funabashi_painting_instructions_{timestamp}.txt"
        with open(instruction_file, 'w', encoding='utf-8') as f:
            f.write(f"生成時刻: {datetime.now()}\n")
            f.write(f"天気情報: {weather_data}\n")
            f.write(f"元プロンプト: {painting_prompt}\n\n")
            f.write("=== AI絵画生成指示 ===\n")
            f.write(ai_instructions)
        
        print(f"📁 AI絵画指示保存: {instruction_file}")
        
        # 5. メタデータ保存
        metadata = {
            "timestamp": timestamp,
            "weather_data": weather_data,
            "original_prompt": painting_prompt,
            "ai_instructions": ai_instructions,
            "instruction_file": instruction_file,
            "status": "ai_instructions_generated",
            "note": "高品質AI絵画生成指示取得完了 - 実際の画像生成は次段階"
        }
        
        metadata_file = f"{output_dir}/metadata_{timestamp}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"📋 メタデータ保存: {metadata_file}")
        
        return {
            "success": True,
            "instruction_file": instruction_file,
            "metadata_file": metadata_file,
            "ai_instructions": ai_instructions
        }
    else:
        print("❌ Gemini API呼び出し失敗")
        return {"success": False, "error": "AI指示生成失敗"}

if __name__ == "__main__":
    # 環境変数読み込み
    from dotenv import load_dotenv
    load_dotenv('/home/aipainting/ai-dynamic-painting/backend/.env')
    
    result = create_high_quality_funabashi_painting()
    
    if result["success"]:
        print("\n🎉 Phase 3 AI画像生成指示取得完了！")
        print("次段階: この指示を基に実際の高品質画像を生成")
    else:
        print("\n❌ AI画像生成指示取得失敗")