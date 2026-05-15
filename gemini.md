# Crop Suggestion System using Gemini AI

This document outlines a simple Crop Suggestion System that utilizes the Google Gemini API to recommend the best crops to plant based on various environmental and soil parameters.

## Prerequisites

1. **Python 3.10+** installed on your system.
2. **Google Gemini API Key**: You need an API key from Google AI Studio.
3. **google-genai** package installed.

You can install the required package using pip:
```bash
pip install google-genai
```

## Python Implementation

Here is a complete Python script that takes in soil and weather conditions and uses Gemini to suggest the most suitable crops. You can copy this code into a new file named `app.py`.

```python
import os
from google import genai

# Configure the API key. 
# It's recommended to set this as an environment variable in your terminal: 
# set GEMINI_API_KEY="your_api_key_here"
API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

if API_KEY == "YOUR_API_KEY_HERE":
    print("WARNING: You are using the placeholder API key 'YOUR_API_KEY_HERE'.")
    print("Please set the GEMINI_API_KEY environment variable or modify app.py directly to use your actual Google Gemini API key.")
    print("The API call will likely fail without a valid key.\n")

client = genai.Client(api_key=API_KEY)

def get_crop_suggestion(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall):
    """
    Uses Gemini to suggest a crop based on environmental and soil parameters.
    """
    prompt = f"""
    You are an expert agricultural agronomist. Based on the following soil and weather conditions, 
    suggest the top 3 most suitable crops to plant. For each crop, provide a brief explanation of why it is suitable.

    Soil and Weather Conditions:
    - Nitrogen (N ratio in soil): {nitrogen}
    - Phosphorus (P ratio in soil): {phosphorus}
    - Potassium (K ratio in soil): {potassium}
    - Temperature: {temperature} °C
    - Humidity: {humidity} %
    - pH Level: {ph}
    - Rainfall: {rainfall} mm

    Format the response clearly with bullet points.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

# Example Usage
if __name__ == "__main__":
    print("--- Crop Suggestion System ---")
    
    # Sample input data
    sample_data = {
        "nitrogen": 90,
        "phosphorus": 42,
        "potassium": 43,
        "temperature": 20.8,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 202.9
    }
    
    print("Analyzing the following conditions:")
    for key, value in sample_data.items():
        print(f"- {key.capitalize()}: {value}")
        
    print("\nFetching suggestions from Gemini...\n")
    
    suggestion = get_crop_suggestion(**sample_data)
    print(suggestion)
```

## How to use

1. Replace `"YOUR_API_KEY_HERE"` with your actual Gemini API key, or set the `GEMINI_API_KEY` environment variable.
2. Modify the `sample_data` dictionary at the bottom of the script to reflect your current soil and weather conditions.
3. Save the Python code to a file like `app.py`.
4. Run the script from your terminal: 
```bash
python app.py
```

## How it works
1. **Inputs**: The system accepts standard NPK values (Nitrogen, Phosphorus, Potassium), Temperature, Humidity, pH, and Rainfall.
2. **Prompt Engineering**: The variables are injected into a prompt where Gemini is instructed to act as an expert agronomist.
3. **Inference**: Gemini processes the combination of these factors and outputs the 3 most viable crops along with explanations of why those crops thrive in the specified conditions.
