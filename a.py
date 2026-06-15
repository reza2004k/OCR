from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google import genai
from google.genai import types
from PIL import Image
import io
import sqlite3
import os
import json

app = Flask(__name__)
CORS(app)

# ۱. دریافت هوشمند کلید API از تنظیمات رندر یا لپ‌تاپ
# این خط در سرور رندر، کلید را از متغیری که در پنل تنظیم کردید می‌خواند
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    # ⚠️ اگر می‌خواهید روی لپ‌تاپ (لوکال یا ngrok) تست کنید، 
    # موقتاً کلید واقعی خود را به جای متن زیر بگذارید.
    # اما حواستان باشد با کلید واقعی آن را روی گیت‌هاب Push نکنید!
    API_KEY = "YOUR_LOCAL_GEMINI_API_KEY_HERE"

client = genai.Client(api_key=API_KEY)

# مسیر دیتابیس را در پوشه موقت سیستم تنظیم می‌کنیم تا رندر خطای دسترسی (Permission) ندهد
DB_PATH = os.path.join('/tmp', 'ocr_stats.db') if os.environ.get('RENDER') else 'ocr_stats.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            accuracy REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ocr', methods=['POST'])
def process_ocr():
    if 'image' not in request.files:
        return jsonify({"error": "هیچ تصویری ارسال نشده است"}), 400
    
    file = request.files['image']
    image_bytes = file.read()
    
    try:
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        prompt = (
            "تو یک سیستم OCR و فرم‌خوان فوق پیشرفته هستی. وظیفه تو استخراج اطلاعات به صورت کلید و مقدار (Key-Value) از این تصویر است.\n\n"
            "دستورالعمل‌های هوشمندانه و حیاتی:\n"
            "1. مبنای تشخیص تو باید 'ساختار فرمی' باشد، نه وجود یک علامت خاص مثل دونقطه. بررسی کن که آیا یک کلمه یا عنوان (مانند نام، تاریخ، شماره فیش، Total، Date و...) به عنوان یک 'کلید' عمل کرده و یک 'مقدار یا داده مشخص' در مقابل, زیر، یا داخل کادر مربوط به خود دارد یا خیر.\n"
            "2. اگر کلمه‌ای در تصویر وجود دارد که کاملاً تنهاست، هیچ داده‌ای به آن منتسب نشده و صرفاً یک متن پراکنده، تیتر بزرگ صفحه، یا راهنمای کلی است، آن را به هیچ وجه استخراج نکن و در جی‌سان ننویس. فقط جفت‌های واقعی کلید و مقدار (Key-Value) را استخراج کن.\n"
            "3. زبان اصلی متن را دقیقاً حفظ کن. اگر کلید یا مقدار در عکس فارسی است، فارسی و اگر انگلیسی است، انگلیسی بنویس. به هیچ عنوان هیچ کلمه‌ای را ترجمه نکن.\n"
            "4. خروجی را دقیقاً به صورت یک شیء JSON با این دو کلید اصلی برگردان:\n"
            "   - 'data': شامل تمام جفت‌های کلید و مقدار استخراج شده واقعی (طبق منطق بالا).\n"
            "   - 'confidence_score': یک عدد اعشاری بین 0 تا 100 نشان‌دهنده میزان دقت تو در تشخیص.\n\n"
            "نکته مهم: هیچ متن اضافی، مقدمه یا علامت مارک‌داون (```json) برنگردان. فقط و فقط JSON خالص."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        result_dict = json.loads(response.text)
        accuracy = result_dict.get('confidence_score', 90.0)
        
        # ذخیره در دیتابیس اصلاح‌شده
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO stats (accuracy) VALUES (?)", (accuracy,))
        conn.commit()
        conn.close()
        
        # استفاده از jsonify برای جلوگیری از خطای ۵۰۰ وب‌سرور رندر
        clean_data = result_dict.get('data', {})
        return jsonify(clean_data), 200
        
    except Exception as e:
        return jsonify({"error": f"خطای سرور پایتون: {str(e)}"}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(accuracy), COUNT(accuracy), MAX(accuracy) FROM stats")
        row = cursor.fetchone()
        conn.close()
        
        average_accuracy = round(row[0], 2) if row[0] else 0
        total_forms = row[1] if row[1] else 0
        max_accuracy = round(row[2], 2) if row[2] else 0
        
        return jsonify({
            "status": "success",
            "average_accuracy_percent": f"{average_accuracy}%",
            "total_processed_forms": total_forms,
            "highest_accuracy_recorded": f"{max_accuracy}%"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)