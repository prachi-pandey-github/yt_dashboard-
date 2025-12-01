# 🚀 Streamlit Deployment Guide

Your YouTube Analytics Chatbot is ready to deploy! Choose from multiple deployment options:

## 🌟 Option 1: Streamlit Cloud (Recommended - Free & Easy)

1. **Push your code to GitHub** ✅ (Already done!)
2. **Visit**: https://share.streamlit.io/
3. **Deploy steps**:
   - Click "New app"
   - Connect your GitHub repository: `prachi-pandey-github/yt_dashboard-`
   - Set main file path: `src/frontend/streamlit_app.py`
   - Add environment variables in the Advanced settings:
     ```
     OPENAI_API_KEY = "your_openai_key_here"
     MONGODB_URI = "your_mongodb_uri_here"
     SECRET_KEY = "your_secret_key_here"
     ```
   - Click "Deploy"

## 🚀 Option 2: Heroku

1. **Install Heroku CLI**: https://devcenter.heroku.com/articles/heroku-cli
2. **Deploy commands**:
   ```bash
   heroku create your-youtube-app-name
   heroku config:set OPENAI_API_KEY=your_key_here
   heroku config:set MONGODB_URI=your_uri_here
   heroku config:set SECRET_KEY=your_secret_here
   git push heroku master
   ```

## 🛤️ Option 3: Railway

1. **Visit**: https://railway.app/
2. **Connect GitHub repo** and deploy automatically
3. **Set environment variables** in Railway dashboard

## 🎨 Option 4: Render

1. **Visit**: https://render.com/
2. **Connect repo** and use the provided `render.yaml`
3. **Configure environment variables** in Render dashboard

## 🏠 Option 5: Local Production

Run with production settings:
```bash
streamlit run src/frontend/streamlit_app.py --server.port=8501 --server.headless=true
```

## 🔐 Environment Variables Needed

For any deployment platform, you'll need:
- `OPENAI_API_KEY`: Your OpenAI API key
- `MONGODB_URI`: Your MongoDB connection string
- `SECRET_KEY`: A secret key for security

## 📱 App Features

Your deployed app will have:
- 🤖 AI-powered YouTube analytics chatbot
- 📊 Interactive data visualizations  
- 🔍 Video search and filtering
- 📈 Channel performance metrics
- 💾 JSON fallback storage (works without MongoDB)