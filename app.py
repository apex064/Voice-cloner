from flask import Flask, render_template, request, send_from_directory
import requests
import os
import uuid

app = Flask(__name__)

# 🔐 Load sensitive info from environment variables
API_KEY = os.environ.get("API_KEY")
VOICE_ID = os.environ.get("VOICE_ID")

# ✅ Safety check to fail fast if keys are missing
if not API_KEY or not VOICE_ID:
    raise RuntimeError("❌ Missing API_KEY or VOICE_ID. Please set them in your environment variables.")

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    filename = None

    if request.method == "POST":
        text = request.form["text"]
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join("static", filename)

        # 🌐 Call ElevenLabs text-to-speech API
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

        # 📝 Debug info for troubleshooting API responses
        print("🔁 ElevenLabs API response status:", response.status_code)
        print("🔍 Content-Type header:", response.headers.get("Content-Type"))
        print("📝 Response preview:", response.text[:200])

        # ✅ Save audio file if response is valid audio
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

if __name__ == "__main__":
    # Bind to the port Render assigns or fallback to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
