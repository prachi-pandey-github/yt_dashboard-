"""
Agent tools for YouTube data analysis - No AWS dependencies
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
import logging
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongodb_client import MongoDBClient
from youtube.channel_manager import ChannelManager

logger = logging.getLogger(__name__)

class YouTubeAnalysisTools:
    """Tools for analyzing YouTube video data"""
    
    def __init__(self):
        self.db_client = MongoDBClient()
        self.channel_manager = ChannelManager()
        self.setup_plotting()
    
    def setup_plotting(self):
        """Setup matplotlib styling"""
        plt.style.use('default')
        sns.set_palette("husl")
    
    def get_channel_mapping(self) -> Dict[str, str]:
        """Get channel name to ID mapping"""
        return {
            "markets": "UCaIGZ2lNpryhA-p9KXr5XNw",
            "bloomberg": "UCaIGZ2lNpryhA-p9KXr5XNw",
            "bloomberg markets": "UCaIGZ2lNpryhA-p9KXr5XNw",
            "aninews": "UCUDXkpsJIdv1aKb1TCN2p0Q",
            "aninewsindia": "UCUDXkpsJIdv1aKb1TCN2p0Q",
            "ani news": "UCUDXkpsJIdv1aKb1TCN2p0Q",
            "test": "UCDANGgqLMuoRfpX75LP7bUQ"
        }
    
    def get_video_count_by_channel(self, channel_name: str) -> Dict[str, Any]:
        """Get count of videos for a specific channel"""
        channel_mapping = self.get_channel_mapping()
        channel_id = channel_mapping.get(channel_name.lower())
        
        if not channel_id:
            return {
                "error": f"Channel '{channel_name}' not found. Available channels: {list(channel_mapping.keys())}"
            }
        
        count = self.db_client.get_video_count_by_channel(channel_id)
        channel_info = self.channel_manager.get_channel_by_id(channel_id)
        
        return {
            "channel_name": channel_info.name if channel_info else channel_name,
            "channel_id": channel_id,
            "total_videos": count,
            "message": f"Found {count} videos from {channel_info.name if channel_info else channel_name}"
        }
    
    def search_videos_by_keyword(self, keywords: List[str], channel_name: Optional[str] = None,
                               hours: Optional[int] = None) -> Dict[str, Any]:
        """Search videos by keywords in title and description"""
        channel_mapping = self.get_channel_mapping()
        channel_id = channel_mapping.get(channel_name.lower()) if channel_name else None
        
        if channel_name and not channel_id:
            return {
                "error": f"Channel '{channel_name}' not found. Available channels: {list(channel_mapping.keys())}"
            }
        
        # Build search query
        query = "|".join(keywords)
        videos = self.db_client.search_videos(query, channel_id, hours)
        
        # Format response
        response = {
            "keywords": keywords,
            "channel": channel_name,
            "time_frame_hours": hours,
            "video_count": len(videos),
            "videos": []
        }
        
        # Add sample videos to response
        for video in videos[:5]:  # Limit to 5 sample videos
            response["videos"].append({
                "title": video.get('title', 'N/A'),
                "url": video.get('url', 'N/A'),
                "upload_date": video.get('upload_date', 'N/A'),
                "view_count": video.get('view_count', 0),
                "channel_title": video.get('channel_title', 'N/A')
            })
        
        return response
    
    def get_upload_statistics(self, channel_name: str, days: int = 7) -> Dict[str, Any]:
        """Get upload statistics and create visualization"""
        channel_mapping = self.get_channel_mapping()
        channel_id = channel_mapping.get(channel_name.lower())
        
        if not channel_id:
            return {
                "error": f"Channel '{channel_name}' not found. Available channels: {list(channel_mapping.keys())}"
            }
        
        # Get videos from database
        videos = self.db_client.get_videos_by_channel(channel_id, 1000)
        
        if not videos:
            return {
                "error": f"No videos found for channel '{channel_name}'"
            }
        
        # Process dates
        dates = []
        view_counts = []
        like_counts = []
        
        for video in videos:
            try:
                date_str = video['upload_date']
                if 'T' in date_str:
                    date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                else:
                    date = datetime.strptime(date_str, '%Y%m%d').date()
                
                dates.append(date)
                view_counts.append(video.get('view_count', 0))
                like_counts.append(video.get('like_count', 0))
            except Exception as e:
                logger.warning(f"Error processing video date: {e}")
                continue
        
        if not dates:
            return {
                "error": "No valid dates found in videos"
            }
        
        # Create DataFrame for analysis
        df = pd.DataFrame({
            'date': dates,
            'views': view_counts,
            'likes': like_counts
        })
        
        # Date distribution
        date_counts = df['date'].value_counts().sort_index()
        
        # Create interactive plot
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Daily Uploads', 'View Distribution', 'Like Distribution', 'Views vs Likes'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Daily uploads
        fig.add_trace(
            go.Bar(x=date_counts.index, y=date_counts.values, name='Daily Uploads'),
            row=1, col=1
        )
        
        # View distribution
        fig.add_trace(
            go.Histogram(x=df['views'], name='View Distribution', nbinsx=20),
            row=1, col=2
        )
        
        # Like distribution
        fig.add_trace(
            go.Histogram(x=df['likes'], name='Like Distribution', nbinsx=20),
            row=2, col=1
        )
        
        # Views vs Likes scatter
        fig.add_trace(
            go.Scatter(x=df['views'], y=df['likes'], mode='markers', name='Views vs Likes'),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=False, title_text=f"Channel Analytics: {channel_name}")
        
        # Convert plot to HTML
        plot_html = fig.to_html(include_plotlyjs='cdn')
        
        # Statistics
        stats = {
            "total_videos_analyzed": len(df),
            "date_range": {
                "start": df['date'].min().isoformat(),
                "end": df['date'].max().isoformat()
            },
            "average_views": df['views'].mean(),
            "average_likes": df['likes'].mean(),
            "total_views": df['views'].sum(),
            "total_likes": df['likes'].sum()
        }
        
        return {
            "channel_name": channel_name,
            "analysis_period_days": days,
            "statistics": stats,
            "upload_distribution": date_counts.to_dict(),
            "plot_html": plot_html
        }
    
    def get_recent_activity(self, hours: int = 24) -> Dict[str, Any]:
        """Get recent video activity across all channels"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get recent videos from all channels
        all_videos = []
        channels = self.channel_manager.get_all_channels()
        
        for channel in channels:
            videos = self.db_client.get_recent_videos(50, channel.channel_id)
            for video in videos:
                try:
                    video_time = datetime.fromisoformat(video['upload_date'].replace('Z', '+00:00'))
                    if video_time >= cutoff_time:
                        all_videos.append({
                            **video,
                            'channel_name': channel.name
                        })
                except:
                    continue
        
        # Sort by upload date
        all_videos.sort(key=lambda x: x['upload_date'], reverse=True)
        
        # Group by channel
        channel_summary = {}
        for video in all_videos:
            channel = video['channel_name']
            if channel not in channel_summary:
                channel_summary[channel] = []
            channel_summary[channel].append(video)
        
        return {
            "time_frame_hours": hours,
            "total_videos": len(all_videos),
            "channels": {
                channel: {
                    "count": len(videos),
                    "recent_titles": [v['title'] for v in videos[:3]]
                }
                for channel, videos in channel_summary.items()
            },
            "recent_videos": all_videos[:10]  # Top 10 most recent
        }
    
    def generate_engagement_report(self) -> Dict[str, Any]:
        """Generate engagement report across all channels"""
        channels = self.channel_manager.get_all_channels()
        report = {}
        
        for channel in channels:
            stats = self.db_client.get_channel_stats(channel.channel_id)
            if stats:
                report[channel.name] = {
                    "total_videos": stats.get('total_videos', 0),
                    "total_views": stats.get('total_views', 0),
                    "total_likes": stats.get('total_likes', 0),
                    "average_views": stats.get('average_views', 0),
                    "average_likes": stats.get('average_likes', 0)
                }
        
        # Create comparison chart
        if report:
            channels = list(report.keys())
            avg_views = [report[channel]['average_views'] for channel in channels]
            avg_likes = [report[channel]['average_likes'] for channel in channels]
            
            fig = go.Figure(data=[
                go.Bar(name='Average Views', x=channels, y=avg_views),
                go.Bar(name='Average Likes', x=channels, y=avg_likes)
            ])
            
            fig.update_layout(
                title='Channel Engagement Comparison',
                barmode='group',
                xaxis_tickangle=-45
            )
            
            plot_html = fig.to_html(include_plotlyjs='cdn')
            
            return {
                "report": report,
                "plot_html": plot_html
            }
        
        return {"error": "No data available for analysis"}