"""
app.py
CodeGuardian AI -- paste code, get a level-appropriate explanation,
complexity analysis, bug flags, suggestions, interview questions, and a
flowchart. Uses Google's Gemini API (free tier available).

Run:
    1. Copy .env.example to .env and add your GEMINI_API_KEY
    2. pip install -r requirements.txt
    3. python app.py
    4. Open http://127.0.0.1:5000
"""

import os
import json
import re

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from prompts import build_prompt

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-flash"

app = Flask(__name__)

if API_KEY:
    genai.configure(api_key=API_KEY)


def _extract_json(raw_text):
    """Gemini is instructed to return raw JSON, but models sometimes wrap it
    in ```json fences anyway -- strip those defensively before parsing."""
    text = raw_text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    return json.loads(text)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    if not API_KEY:
        return jsonify({
            "error": "Server has no GEMINI_API_KEY configured. Add one to your .env file "
                     "(see .env.example) or your hosting provider's environment variables."
        }), 500

    data = request.get_json(force=True, silent=True) or {}
    code = (data.get("code") or "").strip()
    level = (data.get("level") or "beginner").strip().lower()

    if not code:
        return jsonify({"error": "No code provided."}), 400

    if len(code) > 12000:
        return jsonify({"error": "That's a lot of code -- please paste under ~12,000 characters at a time."}), 400

    prompt = build_prompt(code, level)

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        raw_text = response.text
    except Exception as e:
        return jsonify({"error": f"AI request failed: {str(e)}"}), 502

    try:
        result = _extract_json(raw_text)
    except (json.JSONDecodeError, AttributeError):
        return jsonify({
            "error": "The AI response wasn't valid JSON. This sometimes happens on very "
                     "unusual input -- try again, or simplify the code snippet."
        }), 502

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
