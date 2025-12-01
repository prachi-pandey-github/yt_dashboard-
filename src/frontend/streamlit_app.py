"""
Streamlit frontend for YouTube Analytics Chatbot - No AWS dependencies
"""
import streamlit as st
import logging
import json
import sys
import os
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.chatbot import YouTubeChatbot
from agents.tools import YouTubeAnalysisTools
from utils.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_session_state():
    """Initialize session state variables"""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = YouTubeChatbot()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'tools' not in st.session_state:
        st.session_state.tools = YouTubeAnalysisTools()

def setup_page():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title="YouTube Analytics Chatbot",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 YouTube Analytics Chatbot")
    st.markdown("""
    **Ask questions about YouTube video data from high-frequency channels**
    
    *Supported Channels:* Bloomberg Markets, ANI News India, and more!
    """)

def render_sidebar():
    """Render sidebar with quick actions and information"""
    with st.sidebar:
        st.header("Quick Actions")
        
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        st.divider()
        
        st.header("Channel Info")
        tools = st.session_state.tools
        channels = tools.channel_manager.get_all_channels()
        
        for channel in channels:
            count = tools.db_client.get_video_count_by_channel(channel.channel_id)
            st.metric(
                label=channel.name,
                value=count
            )
        
        st.divider()
        
        st.header("Example Queries")
        example_queries = [
            "How many videos from markets channel?",
            "Search videos about USA in ANI News from last 24 hours",
            "Show me statistics for Bloomberg Markets",
            "What's the recent activity?",
            "Generate engagement report"
        ]
        
        for query in example_queries:
            if st.button(f"\"{query}\"", key=query):
                st.session_state.messages.append({"role": "user", "content": query})
                process_user_query(query)

def render_chat_messages():
    """Render chat messages only"""
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def render_chat_input():
    """Render chat input outside of containers"""
    # Chat input
    if prompt := st.chat_input("Ask about YouTube video data..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process and display assistant response
        with st.spinner("Analyzing..."):
            response = process_user_query(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)

def process_user_query(query: str) -> str:
    """Process user query and return response"""
    try:
        response = st.session_state.chatbot.process_query(query)
        st.session_state.messages.append({"role": "assistant", "content": response})
        return response
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        return error_msg

def render_analytics_dashboard():
    """Render analytics dashboard in a separate tab"""
    st.header("📈 Analytics Dashboard")
    
    tools = st.session_state.tools
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Channel Statistics")
        channel_stats = tools.generate_engagement_report()
        
        if 'report' in channel_stats:
            for channel_name, stats in channel_stats['report'].items():
                with st.expander(f"📺 {channel_name}"):
                    st.metric("Total Videos", stats['total_videos'])
                    st.metric("Total Views", f"{stats['total_views']:,}")
                    st.metric("Average Views", f"{stats['average_views']:,.0f}")
                    st.metric("Average Likes", f"{stats['average_likes']:,.0f}")
    
    with col2:
        st.subheader("Recent Activity")
        recent_activity = tools.get_recent_activity(hours=24)
        
        st.metric("Videos Last 24h", recent_activity['total_videos'])
        
        for channel, data in recent_activity['channels'].items():
            st.write(f"**{channel}**: {data['count']} videos")
            for title in data['recent_titles'][:2]:
                st.caption(f"• {title[:60]}...")
    
    # Display plots if available
    st.subheader("Visualizations")
    
    # Channel comparison plot
    if 'plot_html' in channel_stats:
        st.components.v1.html(channel_stats['plot_html'], height=600)
    
    # Individual channel statistics
    st.subheader("Detailed Channel Analytics")
    channel_option = st.selectbox(
        "Select Channel",
        ["markets", "aninewsindia"]
    )
    
    if st.button("Generate Channel Report"):
        with st.spinner("Generating report..."):
            try:
                st.write(f"📊 Generating report for channel: {channel_option}")
                tools = YouTubeAnalysisTools()
                stats = tools.get_upload_statistics(channel_option, days=30)
                
                st.write("Debug - Stats received:", stats)
                
                if 'error' in stats:
                    st.error(f"Error: {stats['error']}")
                elif 'plot_html' in stats:
                    st.components.v1.html(stats['plot_html'], height=800)
                elif 'statistics' in stats:
                    st.json(stats['statistics'])
                else:
                    st.warning("No data received from the report generation")
                    
            except Exception as e:
                st.error(f"Exception occurred: {str(e)}")
                st.exception(e)

def main():
    """Main application function"""
    initialize_session_state()
    setup_page()
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Dashboard", "ℹ️ About"])
    
    with tab1:
        render_sidebar()
        render_chat_messages()
    
    with tab2:
        render_analytics_dashboard()
    
    with tab3:
        st.header("About This Application")
        st.markdown("""
        This YouTube Analytics Chatbot provides real-time monitoring and analysis of high-frequency YouTube channels.
        
        **Features:**
        - 🔔 Real-time video monitoring via WebSub
        - 🗄️ Cloud-native data storage
        - 🤖 AI-powered analytics chatbot
        - 📊 Interactive visualizations
        - 🔍 Advanced search capabilities
        
        **Technology Stack:**
        - **Backend**: FastAPI, Python, MongoDB
        - **Frontend**: Streamlit
        - **AI/ML**: LangChain, OpenAI
        - **Deployment**: Railway/Render (Cloud-agnostic)
        
        **Monitored Channels:**
        - Bloomberg Markets (@markets)
        - ANI News India (@ANINewsIndia)
        - Test channels for validation
        """)
        
        st.info("💡 **Tip**: Use the chat interface to ask natural language questions about your YouTube data!")
    
    # Chat input outside of tabs
    render_chat_input()

if __name__ == "__main__":
    main()