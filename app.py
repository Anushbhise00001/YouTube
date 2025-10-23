from flask import Flask, render_template, request, jsonify
from fetcher import get_video_metadata, get_authenticated_service
import sys
import io
import os

# Flask app with correct template folder
app = Flask(__name__, template_folder="templates")

# Initialize YouTube service once
youtube_service = get_authenticated_service()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/fetch", methods=["POST"])
def fetch():
    data = request.get_json()
    video_id = data.get("video_id")

    if not video_id:
        return jsonify({"error": "No Video ID provided"}), 400

    if not youtube_service:
        return jsonify({"error": "YouTube service not available"}), 500

    # Capture any print statements from fetcher.py (if still present)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        result = get_video_metadata(youtube_service, video_id)
        # If fetcher.py prints output, capture it
        printed_output = sys.stdout.getvalue()
        if printed_output:
            result = printed_output
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        sys.stdout = old_stdout

if __name__ == "__main__":
    # Replit standard host/port
    app.run(host="0.0.0.0", port=8080)
