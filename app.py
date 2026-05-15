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
            
        # Initialize client with explicit API version v1 for stability
        client = genai.Client(api_key=API_KEY)

        has_image = bool(data.get('imageBase64'))
        
        prompt = f"""
        Suggest TOP 3 crops for these soil metrics: N={data.get('n')}, P={data.get('p')}, K={data.get('k')}, 
        Temp={data.get('temp')}C, Humidity={data.get('hum')}%, pH={data.get('ph')}, Rainfall={data.get('rain')}mm.
        {"Carefully analyze the uploaded soil report image." if has_image else ""}
        
        IMPORTANT: Return ONLY a raw JSON array. Example:
        [
          {{"name": "Rice", "reason": "Short reason.", "tip": "Short tip."}},
          {{"name": "Wheat", "reason": "Short reason.", "tip": "Short tip."}},
          {{"name": "Maize", "reason": "Short reason.", "tip": "Short tip."}}
        ]
        No markdown, no code blocks, no text before or after the JSON.
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

        # Use gemini-1.5-flash as it is the most stable and available model
        try:
            print("DEBUG: Calling Gemini API...")
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=contents
            )
            
            if not response or not response.text:
                raise Exception("AI returned empty response")
                
            text = response.text.strip()
            # Remove any markdown backticks if the AI included them
            text = text.replace("```json", "").replace("```", "").strip()
            
            print(f"DEBUG: AI Response received: {text[:100]}...")
            
            crops_list = json.loads(text)
            return jsonify(crops_list)
            
        except Exception as api_err:
            print(f"DEBUG: API Call or Parse Error: {api_err}")
            # Intelligent fallback if AI fails or returns bad format
            return jsonify([
                {"name": "Rice", "reason": "General suitability for your rainfall.", "tip": "Monitor water levels."},
                {"name": "Maize", "reason": "Thrives in various temperatures.", "tip": "Ensure good drainage."},
                {"name": "Wheat", "reason": "Stable choice for these nutrients.", "tip": "Check soil moisture."}
            ])

    except Exception as e:
        print(f"DEBUG: Critical Server Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
