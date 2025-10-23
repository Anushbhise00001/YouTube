import googleapiclient.discovery
import googleapiclient.errors
import os
import pickle
import google.auth.transport.requests
from datetime import datetime

# Scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def get_authenticated_service():
    """
    Authenticate and return the YouTube API service.
    """
    credentials = None
    token_path = os.path.join(os.getcwd(), "token.pickle")  # Works with Replit

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            credentials = pickle.load(token)

        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(google.auth.transport.requests.Request())
    else:
        print("❌ Error: 'token.pickle' not found. Run authentication first.")
        return None

    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)


def get_video_metadata(youtube_service, video_id):
    """
    Fetch metadata for a video and return as a string (instead of printing).
    """
    output = []
    try:
        request = youtube_service.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response = request.execute()

        if not response["items"]:
            return f"⚠️ No video found with ID '{video_id}'."

        video_data = response["items"][0]
        snippet = video_data["snippet"]
        stats = video_data.get("statistics", {})
        content = video_data["contentDetails"]

        published_datetime = datetime.strptime(snippet["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
        formatted_date = published_datetime.strftime("%d %B %Y, %I:%M %p")

        output.append(f"Title: {snippet['title']}\n")
        output.append(f"Description:\n{snippet.get('description', 'No description available.')}\n")
        output.append(f"Tags: {', '.join(snippet.get('tags', [])) or 'No tags found.'}\n")
        output.append("Statistics:")
        output.append(f"  Views: {stats.get('viewCount', 'N/A')}")
        output.append(f"  Likes: {stats.get('likeCount', 'N/A')}")
        output.append(f"  Comments: {stats.get('commentCount', 'N/A')}")
        output.append(f"Duration: {content['duration']}")
        output.append(f"📅 Published At: {formatted_date}")

        return "\n".join(output)

    except googleapiclient.errors.HttpError as e:
        return f"❌ HTTP Error: {e}"
    except Exception as e:
        return f"⚠️ Unexpected Error: {e}"


if __name__ == "__main__":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    youtube_service = get_authenticated_service()

    if youtube_service:
        print("✅ YouTube API connected successfully!\n")
        print("👉 Enter YouTube Video IDs to fetch metadata (type 'exit' to quit):\n")

        while True:
            try:
                video_id = input("🎬 Video ID: ").strip()
                if video_id.lower() == "exit":
                    print("👋 Exiting...")
                    break
                elif video_id == "":
                    continue
                else:
                    result = get_video_metadata(youtube_service, video_id)
                    print(result)
                    print("============================\n")
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
