"""
AI Chatbot for YouTube analytics - No AWS dependencies
"""
import streamlit as st
import logging
from typing import Dict, Any
import json

# Use LangChain instead of Google ADK
from langchain_openai import OpenAI, ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import Tool
import logging

from .tools import YouTubeAnalysisTools
from utils.config import get_settings

logger = logging.getLogger(__name__)

class YouTubeChatbot:
    """YouTube analytics chatbot using LangChain"""
    
    def __init__(self):
        self.settings = get_settings()
        self.tools = YouTubeAnalysisTools()
        self.llm = self._setup_llm()
        self.agent = self._setup_agent()
    
    def _setup_llm(self):
        """Setup language model"""
        api_key = self.settings.effective_openai_api_key
        if api_key:
            return ChatOpenAI(
                openai_api_key=api_key,
                model_name="gpt-3.5-turbo",
                temperature=0
            )
        else:
            # Fallback to a simple rule-based system
            return None
    
    def _setup_agent(self):
        """Setup LangChain agent with tools"""
        if not self.llm:
            return None
        
        tools = [
            Tool(
                name="get_video_count_by_channel",
                func=self.tools.get_video_count_by_channel,
                description="Get the total number of videos saved in database for a specific YouTube channel. Input should be the channel name like 'markets' or 'aninewsindia'."
            ),
            Tool(
                name="search_videos_by_keyword",
                func=self.tools.search_videos_by_keyword,
                description="Search videos by keywords in title and description. Input should be a JSON string with 'keywords' list and optional 'channel_name' and 'hours'."
            ),
            Tool(
                name="get_upload_statistics",
                func=self.tools.get_upload_statistics,
                description="Get upload statistics and visualization for a channel. Input should be a JSON string with 'channel_name' and optional 'days'."
            ),
            Tool(
                name="get_recent_activity",
                func=self.tools.get_recent_activity,
                description="Get recent video activity across all channels. Input should be the number of hours to look back."
            ),
            Tool(
                name="generate_engagement_report",
                func=self.tools.generate_engagement_report,
                description="Generate engagement report across all channels. No input required."
            )
        ]
        
        # Create a simple agent wrapper class
        class SimpleAgent:
            def __init__(self, llm, tools):
                self.llm = llm
                self.tools = {tool.name: tool for tool in tools}
                
            def run(self, input):
                # For now, use the LLM directly without complex agent logic
                # In a production system, you'd implement ReAct logic here
                try:
                    if self.llm:
                        response = self.llm.invoke([HumanMessage(content=input)])
                        return response.content
                    else:
                        return "I'm sorry, but I don't have access to an LLM right now."
                except Exception as e:
                    return f"I encountered an error: {str(e)}"
        
        return SimpleAgent(self.llm, tools)
    
    def process_query(self, query: str) -> str:
        """Process user query using the agent or fallback system"""
        try:
            if self.agent:
                # Use LangChain agent
                response = self.agent.run(input=query)
                return response
            else:
                # Fallback to rule-based system
                return self._fallback_response(query)
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _fallback_response(self, query: str) -> str:
        """Fallback response system when no LLM is available"""
        query_lower = query.lower()
        
        # Channel count queries
        if any(word in query_lower for word in ['how many', 'count', 'number']) and 'video' in query_lower:
            if 'markets' in query_lower or 'bloomberg' in query_lower:
                result = self.tools.get_video_count_by_channel('markets')
                return f"📊 {result['message']}"
            elif 'aninews' in query_lower or 'ani news' in query_lower:
                result = self.tools.get_video_count_by_channel('aninewsindia')
                return f"📊 {result['message']}"
            else:
                return "I can help you get video counts for specific channels. Please specify which channel you're interested in: 'markets' or 'aninewsindia'."
        
        # Search queries
        elif any(word in query_lower for word in ['search', 'find', 'look for']):
            # Simple keyword extraction
            keywords = []
            channel = None
            
            if 'usa' in query_lower or 'united states' in query_lower:
                keywords.append('usa')
            if 'india' in query_lower:
                keywords.append('india')
            if 'market' in query_lower:
                keywords.append('market')
            if 'news' in query_lower:
                keywords.append('news')
            
            if 'channel' in query_lower:
                if 'markets' in query_lower:
                    channel = 'markets'
                elif 'aninews' in query_lower:
                    channel = 'aninewsindia'
            
            if not keywords:
                keywords = ['news']  # Default keyword
            
            result = self.tools.search_videos_by_keyword(keywords, channel, hours=24)
            
            if 'error' in result:
                return f"❌ {result['error']}"
            else:
                return f"🔍 Found {result['video_count']} videos matching your search. Recent videos: {', '.join([v['title'][:50] + '...' for v in result['videos'][:3]])}"
        
        # Statistics queries
        elif any(word in query_lower for word in ['statistic', 'analytics', 'report', 'dashboard']):
            if 'markets' in query_lower:
                result = self.tools.get_upload_statistics('markets')
            elif 'aninews' in query_lower:
                result = self.tools.get_upload_statistics('aninewsindia')
            else:
                result = self.tools.generate_engagement_report()
            
            if 'error' in result:
                return f"❌ {result['error']}"
            else:
                return "📈 I've generated analytics for you. Check the charts section for visualizations."
        
        # Recent activity
        elif any(word in query_lower for word in ['recent', 'latest', 'new', 'activity']):
            result = self.tools.get_recent_activity(hours=24)
            return f"🆕 In the last 24 hours, {result['total_videos']} new videos were published across all channels."
        
        # Default response
        else:
            return """🤖 I'm your YouTube analytics assistant! I can help you with:

• 📊 Video counts by channel
• 🔍 Search videos by keywords  
• 📈 Channel statistics and analytics
• 🆕 Recent video activity
• 📉 Engagement reports

Try asking:
- "How many videos from Bloomberg Markets are in the database?"
- "Search for videos about USA in ANI News from the last 24 hours"
- "Show me statistics for markets channel"
- "What's the recent activity?"""""