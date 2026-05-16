from flask import Flask, render_template, request, jsonify
import os
from google import genai
import base64
import io
from PIL import Image
import json
import random

app = Flask(__name__)

# Primary API Key
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCBCch_wDvMHzpBJmn-WIsj4x_9dFPEN8k")

@app.route('/')
def index():
    return "Smart Farming API is Live! v5"

@app.route('/api/suggest', methods=['POST'])
def api_suggest():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data"}), 400
            
        client = genai.Client(api_key=API_KEY)
        lang_code = data.get('lang', 'en')
        
        # Mapping for languages
        lang_map = {'hi': 'Hindi', 'te': 'Telugu', 'en': 'English'}
        target_lang = lang_map.get(lang_code, 'English')
        
        # Create an even more forceful prompt for translation
        prompt = f"""
        YOU ARE AN EXPERT INDIAN AGRONOMIST. 
        Soil Data: N={data.get('n')}, P={data.get('p')}, K={data.get('k')}, 
        Temp={data.get('temp')}C, Humidity={data.get('hum')}%, pH={data.get('ph')}, Rain={data.get('rain')}mm.
        
        CRITICAL INSTRUCTION: Your entire response MUST be in the {target_lang} language. 
        The crop "name", the "reason", and the "tip" MUST ALL BE WRITTEN IN {target_lang} SCRIPT.
        
        Example for {target_lang}:
        [
          {{"name": "[Name in {target_lang}]", "reason": "[Reason in {target_lang}]", "tip": "[Tip in {target_lang}]"}}
        ]
        
        Return ONLY the raw JSON array.
        """

        contents = [prompt]
        if data.get('imageBase64'):
            try:
                b64 = data['imageBase64'].split(",")[-1]
                img = Image.open(io.BytesIO(base64.b64decode(b64)))
                contents.append(img)
            except: pass

        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=contents
            )
            
            text = response.text.strip().replace("```json", "").replace("```", "").strip()
            return jsonify(json.loads(text))
            
        except Exception as e:
            # Localized Fallback
            if lang_code == 'hi':
                return jsonify([{"name": "चावल", "reason": "उपयुक्त मिट्टी।", "tip": "पानी का ध्यान रखें।"}])
            elif lang_code == 'te':
                return jsonify([{"name": "వరి", "reason": "అనుకూలమైన నేల.", "tip": "నీటిని పర్యవేక్షించండి."}])
            else:
                return jsonify([{"name": "Rice", "reason": "Suitable soil.", "tip": "Monitor water."}])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
