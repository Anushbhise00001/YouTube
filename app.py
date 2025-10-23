from flask import Flask, render_template, request, jsonify
from fetcher import get_video_metadata, get_authenticated_service
import sys
import io
import os
import base64

# Flask app with correct template folder
app = Flask(__name__, template_folder="templates")

# Lazily initialize YouTube service to avoid interactive OAuth at import time
youtube_service = None

def get_cached_service():
    global youtube_service
    if youtube_service:
        return youtube_service

    # If you set TOKEN_PICKLE_B64 (base64 of token.pickle) as a Render/Heroku secret,
    # write it to token.pickle so fetcher can load it.
    token_b64 = os.environ.get("TOKEN_PICKLE_B64")
    if token_b64:
        token_path = os.path.join(os.getcwd(), "token.pickle")
        if not os.path.exists(token_path):
            with open(token_path, "wb") as f:
                f.write(base64.b64decode(token_b64))

    # If you set CLIENT_SECRETS_JSON env var (raw JSON), write it to client_secrets.json
    client_json = os.environ.get("CLIENT_SECRETS_JSON")
    if client_json:
        cs_path = os.path.join(os.getcwd(), "client_secrets.json")
        if not os.path.exists(cs_path):
            with open(cs_path, "w", encoding="utf-8") as f:
                f.write(client_json)

    youtube_service = get_authenticated_service()
    return youtube_service

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/fetch", methods=["POST"])
def fetch():
    data = request.get_json()
    video_id = data.get("video_id")

    if not video_id:
        return jsonify({"error": "No Video ID provided"}), 400

    try:
        svc = get_cached_service()
    except Exception as e:
        return jsonify({"error": f"Failed to init YouTube service: {e}"}), 500

    try:
        result = get_video_metadata(svc, video_id)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Use PORT env var (Render provides $PORT). Default 8080 for local dev.
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
