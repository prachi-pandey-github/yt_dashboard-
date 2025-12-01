# YouTube Real-Time Monitoring System

A cloud-native system for real-time YouTube video monitoring with Agentic AI capabilities.

## Features

- 🔔 **Real-time YouTube Monitoring**: WebSub webhooks for instant video notifications
- 🗄️ **Cloud-Native Storage**: MongoDB with idempotent operations
- 🔐 **Secure API**: FastAPI with token-based authentication
- 🤖 **Agentic AI Chatbot**: Google ADK-powered intelligent querying
- ☁️ **Serverless Ready**: Deployable on GCP Cloud Functions, AWS Lambda
- 📊 **Data Visualization**: Interactive charts and analytics
- 🔄 **Idempotent Processing**: Handles duplicate events gracefully

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/prachi-pandey-github/yt_dashboard-.git
   cd yt_dashboard-
   ```

2. **Set up environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the Streamlit app**
   ```bash
   cd src/frontend
   streamlit run streamlit_app.py
   ```

### Streamlit Cloud Deployment

1. **Fork this repository** on GitHub

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your forked repository
   - Set main file path to: `src/frontend/streamlit_app.py`

3. **Configure secrets in Streamlit Cloud**
   - In your Streamlit Cloud app settings, add these secrets:
   ```toml
   YOUTUBE_API_KEY = "your_youtube_api_key_here"
   OPENAI_API_KEY = "your_openai_api_key_here"
   MONGODB_URI = "your_mongodb_connection_string"
   DATABASE_NAME = "youtube_monitoring"
   ```

4. **Get your API keys**
   - **YouTube API**: [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - **OpenAI API**: [OpenAI Platform](https://platform.openai.com/api-keys)
   - **MongoDB**: [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (free tier available)

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | ✅ |
| `OPENAI_API_KEY` | OpenAI API key for chatbot | ✅ |
| `MONGODB_URI` | MongoDB connection string | ✅ |
| `DATABASE_NAME` | Database name (default: youtube_monitoring) | ✅ |

## Architecture
