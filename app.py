from flask import Flask, render_template, request, send_from_directory
import requests
import os
import uuid

app = Flask(__name__)

# 🔐 Load from environment variables
API_KEY = os.environ.get("API_KEY")
VOICE_ID = os.environ.get("VOICE_ID")

# ✅ Safety check if missing
if not API_KEY or not VOICE_ID:
    raise RuntimeError("❌ Missing API_KEY or VOICE_ID. Set them in Render environment.")

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    filename = None

    if request.method == "POST":
        text = request.form["text"]
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join("static", filename)

        # 🌐 Make ElevenLabs request
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={
                "xi-api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.7,
                    "similarity_boost": 0.75
                }
            }
        )

        print("🔁 ElevenLabs API response:", response.status_code)
        print("🔍 Content-Type:", response.headers.get("Content-Type"))
        print("📝 Response Preview:", response.text[:200])

        # ✅ Save only if valid audio
        if response.status_code == 200 and "audio/mpeg" in response.headers.get("Content-Type", ""):
            with open(filepath, "wb") as f:
                f.write(response.content)
            message = "✅ Speech generated successfully!"
        else:
            message = f"❌ API Error: {response.status_code} - {response.text}"
            filename = None

    return render_template("index.html", message=message, filename=filename)

@app.route("/static/<path:filename>")
def serve_audio(filename):
    return send_from_directory("static", filename)
