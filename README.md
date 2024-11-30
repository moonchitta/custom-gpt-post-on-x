# Twitter API OAuth 2.0 App with customGPT Actions Integration

This project implements an OAuth 2.0-based authentication flow for Twitter API using Flask and Python, enabling users to post tweets, upload media, and interact with Twitter via a secure API. The core functionality of this project is designed to integrate with **customGPT Actions**, allowing users to automate and extend their workflows through GPT-based actions.

## Key Features

- **OAuth 2.0 Authentication**: Secure login via Twitter API with code verification, token generation, and session management.
- **Tweet Posting**: Post tweets on behalf of authenticated users, with or without media.
- **Media Upload**: Upload and associate images, videos, or GIFs to tweets.
- **CustomGPT Actions Integration**: Automate Twitter actions using GPT models to generate tweets and interact with Twitter data.

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- `pip` for installing Python packages
- Flask
- Twitter API credentials (Client ID, Client Secret, Access Token, and Access Token Secret)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/twitter-api-oauth.git
   cd twitter-api-oauth
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root of the project and add the following environment variables with your Twitter API credentials:
   ```ini
   FLASK_SECRET_KEY=your_secret_key
   CLIENT_ID=your_twitter_client_id
   CLIENT_SECRET=your_twitter_client_secret
   ACCESS_TOKEN=your_twitter_access_token
   ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
   REDIRECT_URI=your_redirect_url
   ```

4. Run the Flask application:
   ```bash
   python app.py
   ```

The application will start running on `http://localhost:5000`.

## Endpoints

### `/startAuth`
- **Method**: `GET`
- **Description**: Starts the OAuth 2.0 authentication flow. Redirects users to Twitter's authorization page.
- **Response**: Returns the authorization URL and state.
  ```json
  {
    "authorization_url": "https://twitter.com/i/oauth2/authorize?response_type=code&client_id=your_client_id&redirect_uri=your_redirect_uri",
    "state": "random_state_value"
  }
  ```

### `/callback`
- **Method**: `GET`
- **Description**: Handles the callback from Twitter after user authorization. Exchanges the authorization code for an access token.
- **Response**: Returns the access token, expiration date, and scope.
  ```json
  {
    "message": "Authentication successful!",
    "access_token": "your_access_token",
    "expires_at": "2024-12-01T00:00:00Z",
    "scope": "users.read tweet.read tweet.write"
  }
  ```

### `/postTweet`
- **Method**: `POST`
- **Description**: Allows the user to post a tweet, optionally with media (image, video, or GIF).
- **Request Body**:
  ```json
  {
    "text": "Your tweet text here",
    "media_url": "https://example.com/image.jpg" 
  }
  ```
- **Response**:
  ```json
  {
    "message": "Tweet posted successfully!",
    "tweet_id": "1234567890",
    "tweet_text": "Your tweet text here",
    "tweet_url": "https://twitter.com/user/status/1234567890"
  }
  ```

## Integration with customGPT Actions

The purpose of this project is to allow **customGPT Actions** to automate Twitter interactions. By integrating with GPT models, users can automate the process of generating tweets or executing other actions based on specific inputs.

### Workflow Example

1. **CustomGPT Action**: Create a tweet based on a topic or user input.
   - **Input**: User provides a topic, and GPT generates a tweet about it.
   - **Output**: The action posts the generated tweet on Twitter via the `/postTweet` endpoint.

2. **Automating Media Tweets**: CustomGPT can be used to automatically generate media-based tweets, including uploading an image or video and associating it with the tweet. For example, GPT can generate a tweet with a relevant image or video based on a user’s request.

### Example Action Flow

1. **User**: "Generate a tweet about the latest tech news."
2. **customGPT**: Generates a tweet text.
3. **API**: Sends the generated text to the `/postTweet` endpoint.
4. **Result**: The tweet is posted on the user's Twitter account.

This integration allows for powerful, automated workflows that make use of the GPT model to generate and post content directly to Twitter.

## Token Management

Tokens are stored in a `token.json` file to maintain user authentication. This allows users to remain authenticated for future requests without needing to reauthorize each time.

- **Save Tokens**: Tokens are saved in `token.json` after the OAuth process completes successfully.
- **Load Tokens**: Tokens can be loaded from `token.json` when making API requests.

## Error Handling

The application includes basic error handling for various scenarios:

- Invalid authorization code or state mismatch in the callback
- Missing tweet text or media URL
- Failure to download or upload media

Each error returns a JSON response with an appropriate error message.

## Security Considerations

- **Session Management**: The Flask session is configured with secure options to prevent session hijacking or cross-site scripting (XSS) attacks.
- **HTTPS**: Ensure that your app is served over HTTPS when using it in production, especially when handling sensitive tokens and user data.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.