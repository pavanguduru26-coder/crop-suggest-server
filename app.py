from flask import Flask, render_template, request, jsonify
import os
from google import genai
import base64
import io
from PIL import Image
import json

app = Flask(__name__)

# Primary API Key
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCBCch_wDvMHzpBJmn-WIsj4x_9dFPEN8k")

@app.route('/')
def index():
    return "Smart Farming API is Live!"

@app.route('/api/suggest', methods=['POST'])
def api_suggest():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400
            
        client = genai.Client(api_key=API_KEY)
        has_image = bool(data.get('imageBase64'))
        lang_code = data.get('lang', 'en')
        
        # Map language codes to names
        lang_map = {'hi': 'Hindi', 'te': 'Telugu', 'en': 'English'}
        target_lang = lang_map.get(lang_code, 'English')
        
        prompt = f"""
        Suggest TOP 3 crops for these soil metrics: N={data.get('n')}, P={data.get('p')}, K={data.get('k')}, 
        Temp={data.get('temp')}C, Humidity={data.get('hum')}%, pH={data.get('ph')}, Rainfall={data.get('rain')}mm.
        {"Analyze the uploaded soil report image." if has_image else ""}
        
        IMPORTANT: Provide the response COMPLETELY in {target_lang} language.
        Return ONLY a raw JSON array of objects with 'name', 'reason', and 'tip' keys.
        Example in {target_lang}:
        [
          {{"name": "...", "reason": "...", "tip": "..."}},
          {{"name": "...", "reason": "...", "tip": "..."}},
          {{"name": "...", "reason": "...", "tip": "..."}}
        ]
        """

        contents = [prompt]
        if has_image:
            try:
                b64_str = data['imageBase64'].split(",")[-1]
                img_data = base64.b64decode(b64_str)
                img = Image.open(io.BytesIO(img_data))
                contents.append(img)
            except Exception as e:
                print(f"DEBUG: Image decode failed: {e}")

        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=contents
            )
            
            if not response or not response.text:
                raise Exception("AI returned empty response")
                
            text = response.text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            
            crops_list = json.loads(text)
            return jsonify(crops_list)
            
        except Exception as api_err:
            print(f"DEBUG: API Call Error: {api_err}")
            # Fallback in English (could be localized if needed)
            return jsonify([
                {"name": "Rice", "reason": "Stable choice.", "tip": "Maintain water."},
                {"name": "Maize", "reason": "Good for climate.", "tip": "Ensure drainage."},
                {"name": "Wheat", "reason": "Nutrient fit.", "tip": "Check moisture."}
            ])

    except Exception as e:
        print(f"DEBUG: Critical Server Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
