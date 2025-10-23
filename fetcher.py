from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient import errors
import os
import pickle

# Scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def get_authenticated_service():
    """
    Authenticate and return the YouTube API service.
    """
    credentials = None
    token_path = os.path.join(os.getcwd(), "token.pickle")

    if os.path.exists(token_path):
        try:
            with open(token_path, "rb") as token:
                credentials = pickle.load(token)
            
            if not credentials or not credentials.valid:
                print("❌ Error: Credentials expired or invalid")
                return None
        except Exception as e:
            print(f"❌ Error loading token.pickle: {str(e)}")
            return None
    else:
        print("❌ Error: 'token.pickle' not found. Run authentication first.")
        return None

    try:
        return build("youtube", "v3", credentials=credentials)
    except Exception as e:
        print(f"❌ Error building YouTube service: {str(e)}")
        return None

def get_video_metadata(youtube_service, video_id):
    """
    Fetch metadata for a video and return formatted data.
    """
    if not youtube_service:
        return "YouTube service not initialized. Check credentials."

    try:
        request = youtube_service.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response = request.execute()

        if not response.get("items"):
            return f"No video found with ID: {video_id}"

        video = response["items"][0]
        snippet = video["snippet"]
        statistics = video["statistics"]
        
        return {
            "title": snippet["title"],
            "views": statistics.get("viewCount", "N/A"),
            "likes": statistics.get("likeCount", "N/A"),
            "comments": statistics.get("commentCount", "N/A"),
            "published": snippet["publishedAt"],
            "description": snippet.get("description", "No description")
        }

    except errors.HttpError as e:
        error_msg = f"YouTube API error: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

if __name__ == "__main__":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Only for local testing
    youtube_service = get_authenticated_service()