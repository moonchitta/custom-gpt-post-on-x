import json
import mimetypes

import requests
from flask import Flask, request, redirect, session, jsonify
from pytwitter import Api
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

# Load environment variables from .env file
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Replace with a secure key

# Twitter API credentials from environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # Replace with your actual callback URL
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")  # Replace with your actual callback URL
CALLBACK_URL = os.getenv("REDIRECT_URI")  # Replace with your actual callback URL
TOKENS_DIR = "tokens"

# Ensure the directory exists
os.makedirs(TOKENS_DIR, exist_ok=True)

# Initialize Twitter API client
api = Api(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, oauth_flow=True, callback_uri=CALLBACK_URL, scopes=["users.read", "tweet.read", "tweet.write"])

# Store user tokens (replace with a database in production)
user_tokens = {}


@app.route('/')
def home():
    """Welcome route."""
    return "Welcome to the Twitter API OAuth 2.0 App!"


@app.route('/startAuth', methods=['GET'])
def start_auth():
    """Step 1: Redirect user to Twitter for authorization."""
    url, code_verifier, state = api.get_oauth2_authorize_url()
    print(f"URL: {url}")
    session['code_verifier'] = code_verifier
    session['state'] = state
    return redirect(url)


@app.route('/callback', methods=['GET'])
def callback():
    """Step 2: Handle callback from Twitter and generate access token."""
    code = request.args.get("code")
    state = request.args.get("state")

    if not code:
        return jsonify({"error": "Authorization code not found in the callback URL."}), 400

    if state != session.get("state"):
        return jsonify({"error": "State mismatch. Possible CSRF attack."}), 400

    # Retrieve the code verifier from the session
    code_verifier = session.pop("code_verifier", None)
    if not code_verifier:
        return jsonify({"error": "Code verifier not found in session."}), 400

    try:
        # Generate the access token using the authorization code and code verifier
        token_response = api.generate_oauth2_access_token(
            response=f"{CALLBACK_URL}?state={state}&code={code}",
            code_verifier=code_verifier, redirect_uri=CALLBACK_URL
        )

        access_token = token_response["access_token"]
        expires_in = token_response.get("expires_in", 7200)
        scope = token_response["scope"]

        # Use timezone-aware datetime for `expires_at`
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Save token information
        save_access_token(access_token, expires_at.isoformat(), scope)

        return jsonify({
            "message": "Authentication successful!",
            "access_token": access_token,
            "expires_at": expires_at.isoformat(),
            "scope": scope
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to generate access token: {str(e)}"}), 500

def save_access_token(access_token, expires_at, scope):
    """Save access token to a single file."""
    token_file = "token.json"
    token_data = {
        "access_token": access_token,
        "expires_at": expires_at,
        "scope": scope
    }
    with open(token_file, "w") as file:
        json.dump(token_data, file, indent=4)

def load_access_token():
    """Load access token from a single JSON file."""
    token_file = "token.json"
    try:
        if os.path.exists(token_file):
            with open(token_file, "r") as file:
                token_data = json.load(file)
                access_token = token_data["access_token"]
                expires_at = datetime.fromisoformat(token_data["expires_at"])
                scope = token_data["scope"]
                return access_token, expires_at, scope
        return None, None, None
    except Exception as e:
        print(f"Error loading access token: {e}")
        return None, None, None

@app.route('/postTweet', methods=['POST'])
def post_tweet():
    try:
        """Post a tweet on behalf of the user."""
        data = request.json
        tweet_text = data.get("text", "").strip()
        media_url = data.get("media_url", None)  # Optional media URL

        if not tweet_text and not media_url:
            return jsonify({"error": "Either tweet text or media_url is required"}), 400

        # Check if a media URL is provided
        media_id = None
        if media_url:
            # Download the media file
            media_response = requests.get(media_url, stream=True)
            if media_response.status_code != 200:
                return jsonify({"error": f"Failed to download media. Status code: {media_response.status_code}"}), 400

            # Save the media temporarily
            from urllib.parse import urlparse
            parsed_url = urlparse(media_url)
            filename = os.path.basename(parsed_url.path)
            media_file_path = os.path.join(os.getcwd(), filename)

            print(f"Saving file at {media_file_path}")

            with open(media_file_path, "wb") as media_file:
                for chunk in media_response.iter_content(chunk_size=8192):
                    media_file.write(chunk)

            # Determine media category based on file type
            mime_type, _ = mimetypes.guess_type(media_file_path)
            if mime_type.startswith("image/"):
                media_category = "tweet_image"
            elif mime_type == "image/gif":
                media_category = "tweet_gif"
            elif mime_type.startswith("video/"):
                media_category = "tweet_video"
            else:
                os.remove(media_file_path)
                return jsonify({"error": "Unsupported media type"}), 400

            print(f"Media Category: {media_category}")

            try:
                # Upload the media to Twitter
                with open(media_file_path, "rb") as media_file:
                    print(f"Uploading media")
                    media_upload_response = api.upload_media_simple(
                        media=media_file,
                        media_category=media_category
                    )

                print(f"Media uploaded successful")
                media_id = media_upload_response.media_id_string
                print(f"Media ID: {media_id}")

                # Remove the temporary media file
                os.remove(media_file_path)
            except Exception as e:
                return jsonify({"error": f"Failed to upload media: {str(e)}"}), 500

        # Create the tweet
        if media_id:
            response = api.create_tweet(text=tweet_text, media_media_ids=[media_id])
        else:
            response = api.create_tweet(text=tweet_text)

        # Extract the tweet ID and text from the response
        tweet_id = response.id
        tweet_text = response.text

        # Construct the full URL of the tweet
        tweet_url = f"https://twitter.com/user/status/{tweet_id}"

        return jsonify({
            "message": "Tweet posted successfully!",
            "tweet_id": tweet_id,
            "tweet_text": tweet_text,
            "tweet_url": tweet_url
        }), 201
    except Exception as e:
        return jsonify({"error": f"Failed to post tweet: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
