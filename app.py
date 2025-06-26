from flask import Flask, render_template, request, send_from_directory
import requests
import os
import uuid

app = Flask(__name__)

API_KEY = "your_elevenlabs_api_key"
VOICE_ID = "your_cloned_voice_id"  # From ElevenLabs

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    filename = None

    if request.method == "POST":
        text = request.form["text"]
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join("static", filename)

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

        with open(filepath, "wb") as f:
            f.write(response.content)

        message = "Speech generated successfully!"

    return render_template("index.html", message=message, filename=filename)

@app.route("/static/<path:filename>")
def serve_audio(filename):
    return send_from_directory("static", filename)
