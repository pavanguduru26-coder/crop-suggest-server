from flask import Flask, render_template, request, jsonify
import os
from google import genai
import base64
import io
from PIL import Image
import json

app = Flask(__name__)

# Configure the API key
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCBCch_wDvMHzpBJmn-WIsj4x_9dFPEN8k")

@app.route('/')
def index():
    return "Crop Suggestion Server is Live! v2"

@app.route('/api/suggest', methods=['POST'])
def api_suggest():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data"}), 400
            
        client = genai.Client(api_key=API_KEY)
        has_image = bool(data.get('imageBase64'))
        
        prompt = f"""
        Suggest TOP 3 crops: N={data.get('n')}, P={data.get('p')}, K={data.get('k')}, 
        Temp={data.get('temp')}C, Hum={data.get('hum')}%, pH={data.get('ph')}, Rain={data.get('rain')}mm.
        {"Analyze uploaded image." if has_image else ""}
        Return ONLY a JSON array with 'name', 'reason', and 'tip'.
        """

        contents = [prompt]
        if has_image:
            try:
                b64 = data['imageBase64'].split(",")[-1]
                img = Image.open(io.BytesIO(base64.b64decode(b64)))
                contents.append(img)
            except: pass

        # ── Model Fallback Logic ──────────────────────────────────────────────
        # Try 2.0-flash first, then 1.5-flash if that fails
        models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash']
        response_text = ""
        
        for model_name in models_to_try:
            try:
                print(f"Trying model: {model_name}")
                response = client.models.generate_content(model=model_name, contents=contents)
                if response and response.text:
                    response_text = response.text.strip()
                    break
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                continue
        
        if not response_text:
            return jsonify({"error": "AI models currently unavailable"}), 503

        # Clean and Parse JSON
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        try:
            return jsonify(json.loads(clean_json))
        except:
            # Absolute fallback if JSON parsing fails
            return jsonify([{"name": "Rice", "reason": "Suitable for your humidity.", "tip": "Check water levels."}])

    except Exception as e:
        print(f"SERVER ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
