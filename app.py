from flask import Flask, render_template, request, jsonify
import os
from google import genai
import base64
import io
from PIL import Image

app = Flask(__name__)

# Configure the API key
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCBCch_wDvMHzpBJmn-WIsj4x_9dFPEN8k")

@app.route('/')
def index():
    return render_template('index.html')

# ── Endpoint for Web UI ───────────────────────────────────────────────────────
@app.route('/suggest', methods=['POST'])
def suggest():
    data = request.json
    client = genai.Client(api_key=API_KEY)

    prompt = f"""
    You are an expert agricultural agronomist. Based on the following soil and weather conditions,
    suggest the top 3 most suitable crops to plant. For each crop, provide a brief explanation.

    Soil and Weather Conditions:
    - Nitrogen (N): {data.get('nitrogen')}
    - Phosphorus (P): {data.get('phosphorus')}
    - Potassium (K): {data.get('potassium')}
    - Temperature: {data.get('temperature')} °C
    - Humidity: {data.get('humidity')} %
    - pH Level: {data.get('ph')}
    - Rainfall: {data.get('rainfall')} mm

    Format the response clearly with bullet points.
    """

    contents = [prompt]

    if data.get('image'):
        try:
            image_b64 = data['image'].split(',')[1]
            image_bytes = base64.b64decode(image_b64)
            img = Image.open(io.BytesIO(image_bytes))
            contents.append("Also consider the following image of the land/soil/crop.")
            contents.append(img)
        except Exception as e:
            print("Image processing error:", e)

    try:
        response = client.models.generate_content(model='gemini-2.5-flash', contents=contents)
        return jsonify({"suggestion": response.text})
    except Exception as e:
        return jsonify({"error": str(e)})

# ── Endpoint for Android App ──────────────────────────────────────────────────
@app.route('/api/suggest', methods=['POST'])
def api_suggest():
    """
    Android app sends JSON:
    {
      "n": "90", "p": "42", "k": "43",
      "temp": "20.8", "hum": "82.0", "ph": "6.5", "rain": "202.9",
      "imageBase64": "<optional base64 string>"
    }
    Returns JSON array:
    [{"name": "Rice", "reason": "...", "tip": "..."}, ...]
    """
    data = request.json
    client = genai.Client(api_key=API_KEY)

    has_image = bool(data.get('imageBase64'))

    prompt = f"""
    You are an expert agronomist.
    {"IMPORTANT: The user uploaded a soil report or land photo. Analyze it as PRIMARY basis." if has_image else ""}

    Soil metrics: N={data.get('n')}, P={data.get('p')}, K={data.get('k')},
    Temp={data.get('temp')}°C, Humidity={data.get('hum')}%, pH={data.get('ph')}, Rainfall={data.get('rain')}mm

    Suggest TOP 3 crops. Reply ONLY with a valid JSON array. Example:
    [
      {{"name": "Rice", "reason": "One short sentence why.", "tip": "One short tip."}},
      {{"name": "Wheat", "reason": "One short sentence why.", "tip": "One short tip."}},
      {{"name": "Maize", "reason": "One short sentence why.", "tip": "One short tip."}}
    ]
    Output ONLY the JSON array. No markdown, no code fences, no extra text.
    """

    contents = [prompt]

    if has_image:
        try:
            image_bytes = base64.b64decode(data['imageBase64'])
            img = Image.open(io.BytesIO(image_bytes))
            contents.append(img)
        except Exception as e:
            print("Image error:", e)

    try:
        response = client.models.generate_content(model='gemini-2.5-flash', contents=contents)
        text = response.text.strip()
        # Strip markdown fences if present
        text = text.replace("```json", "").replace("```", "").strip()
        import json
        crops = json.loads(text)
        return jsonify(crops)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', debug=False, port=port)
