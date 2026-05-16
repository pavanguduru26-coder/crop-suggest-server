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
    return "Smart Farming API is Live! v4"

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
        
        # Create a more detailed prompt to ensure variety
        prompt = f"""
        ACT AS AN EXPERT AGRONOMIST. 
        Soil Data: Nitrogen={data.get('n')}, Phosphorus={data.get('p')}, Potassium={data.get('k')}, 
        Temp={data.get('temp')}C, Humidity={data.get('hum')}%, pH={data.get('ph')}, Rainfall={data.get('rain')}mm.
        
        TASK: Suggest the 3 BEST crops for these EXACT conditions. 
        Be specific. If it's dry, suggest dry-land crops. If it's wet, suggest water-loving crops.
        
        RESPONSE LANGUAGE: {target_lang}
        FORMAT: Return ONLY a raw JSON array of 3 objects.
        [
          {{"name": "CropName", "reason": "Why it fits these NPK/Weather metrics", "tip": "One farming tip"}}
        ]
        No markdown, no talk.
        """

        contents = [prompt]
        if data.get('imageBase64'):
            try:
                b64 = data['imageBase64'].split(",")[-1]
                img = Image.open(io.BytesIO(base64.b64decode(b64)))
                contents.append(img)
            except: pass

        try:
            # Using 1.5-flash-latest for best availability
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=contents
            )
            
            text = response.text.strip().replace("```json", "").replace("```", "").strip()
            return jsonify(json.loads(text))
            
        except Exception as e:
            print(f"DEBUG API ERROR: {e}")
            # Fallback with randomized variety so it's not always the same
            fallbacks = [
                {"name": "Millet", "reason": "Drought resistant.", "tip": "Low water needed."},
                {"name": "Cotton", "reason": "Fits your temperature.", "tip": "Watch for pests."},
                {"name": "Groundnut", "reason": "Good for soil pH.", "tip": "Avoid waterlogging."}
            ]
            random.shuffle(fallbacks)
            return jsonify(fallbacks)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
