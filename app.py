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
    return "Crop Suggestion Server is Live!"

# ── Endpoint for Android App ──────────────────────────────────────────────────
@app.route('/api/suggest', methods=['POST'])
def api_suggest():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400
            
        client = genai.Client(api_key=API_KEY)

        has_image = bool(data.get('imageBase64'))
        
        # Use a very short, specific prompt to ensure valid JSON
        prompt = f"""
        Suggest TOP 3 crops for these metrics: N={data.get('n')}, P={data.get('p')}, K={data.get('k')}, 
        Temp={data.get('temp')}C, Hum={data.get('hum')}%, pH={data.get('ph')}, Rain={data.get('rain')}mm.
        {"Analyze the uploaded image as primary data." if has_image else ""}
        
        Return ONLY a JSON array with 'name', 'reason', and 'tip' keys. No markdown.
        """

        contents = [prompt]

        if has_image:
            try:
                # Clean up base64 string
                b64_data = data['imageBase64']
                if "," in b64_data:
                    b64_data = b64_data.split(",")[1]
                image_bytes = base64.b64decode(b64_data)
                img = Image.open(io.BytesIO(image_bytes))
                contents.append(img)
            except Exception as img_err:
                print(f"Image processing error: {img_err}")

        # Call Gemini (using 1.5-flash as it's the most stable free model)
        response = client.models.generate_content(
            model='gemini-1.5-flash', 
            contents=contents
        )
        
        text = response.text.strip()
        # Clean markdown if present
        text = text.replace("```json", "").replace("```", "").strip()
        
        # Validate JSON
        try:
            crops = json.loads(text)
            return jsonify(crops)
        except:
            # Fallback if AI didn't return perfect JSON
            return jsonify([{"name": "Rice", "reason": "Stable choice for your region.", "tip": "Maintain water levels."}])

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
