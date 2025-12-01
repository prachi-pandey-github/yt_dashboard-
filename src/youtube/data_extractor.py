"""
YouTube data extraction using yt-dlp and YouTube Data API
"""
import os
import asyncio
import aiohttp
from typing import List, Dict, Optional
import yt_dlp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import VideoMetadata
from utils.config import get_settings
from youtube.channel_manager import ChannelManager

logger = logging.getLogger(__name__)

class YouTubeDataExtractor:
    """Extract YouTube video data using multiple methods"""
    
    def __init__(self):
        self.settings = get_settings()
        self.channel_manager = ChannelManager()
        self.youtube_api = None
        self._initialize_youtube_api()
    
    def _initialize_youtube_api(self):
        """Initialize YouTube Data API client"""
        try:
            api_key = self.settings.effective_youtube_api_key
            if api_key:
                self.youtube = build('youtube', 'v3',
                                   developerKey=api_key)
                logger.info("✅ YouTube Data API initialized")
        except Exception as e:
            logger.warning(f"⚠️ YouTube Data API initialization failed: {e}")
    
    async def get_channel_videos_ytdlp(self, channel_handle: str, 
                                     max_results: int = 100) -> List[Dict]:
        """Get recent videos from a channel using yt-dlp"""
        ydl_opts = {
            'extract_flat': True,
            'force_json': True,
            'quiet': True,
            'no_warnings': True,
            'playlistend': max_results,
        }
        
        videos = []
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                channel_url = f"https://www.youtube.com/{channel_handle}"
                info = await asyncio.to_thread(ydl.extract_info, channel_url, download=False)
                
                if 'entries' in info:
                    for entry in info['entries'][:max_results]:
                        if entry.get('url'):
                            video_data = await self.get_video_details(entry['url'])
                            if video_data:
                                videos.append(video_data)
                                # Small delay to be respectful to YouTube
                                await asyncio.sleep(0.1)
                
                logger.info(f"📹 Extracted {len(videos)} videos from {channel_handle}")
                
        except Exception as e:
            logger.error(f"❌ Error extracting videos from {channel_handle}: {e}")
        
        return videos
    
    async def get_video_details(self, video_url: str) -> Optional[Dict]:
        """Get detailed video information using yt-dlp"""
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, video_url, download=False)
                
                # Convert upload_date to ISO format if needed
                upload_date = info.get('upload_date', '')
                if upload_date and len(upload_date) == 8:  # YYYYMMDD format
                    upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}T00:00:00Z"
                
                return {
                    "video_id": info.get('id'),
                    "title": info.get('title', 'Unknown Title'),
                    "url": video_url,
                    "upload_date": upload_date,
                    "view_count": info.get('view_count', 0),
                    "like_count": info.get('like_count', 0),
                    "description": info.get('description', ''),
                    "channel_id": info.get('channel_id'),
                    "channel_title": info.get('channel', 'Unknown Channel'),
                    "thumbnail_url": info.get('thumbnail'),
                    "duration": info.get('duration_string'),
                    "tags": info.get('tags', []),
                    "category_id": str(info.get('category', ''))
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting video details for {video_url}: {e}")
            return None
    
    async def get_channel_videos_api(self, channel_id: str, 
                                   max_results: int = 50) -> List[Dict]:
        """Get channel videos using YouTube Data API"""
        if not self.youtube_api:
            logger.warning("YouTube Data API not available")
            return []
        
        videos = []
        try:
            # First, get the uploads playlist ID
            channel_response = self.youtube_api.channels().list(
                id=channel_id,
                part='contentDetails'
            ).execute()
            
            if not channel_response.get('items'):
                return videos
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            playlist_response = self.youtube_api.playlistItems().list(
                playlistId=uploads_playlist_id,
                part='snippet',
                maxResults=max_results
            ).execute()
            
            for item in playlist_response.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                video_data = await self.get_video_details_api(video_id)
                if video_data:
                    videos.append(video_data)
            
            logger.info(f"📹 API extracted {len(videos)} videos from channel {channel_id}")
            
        except HttpError as e:
            logger.error(f"❌ YouTube API error for channel {channel_id}: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error getting channel videos: {e}")
        
        return videos
    
    async def get_video_details_api(self, video_id: str) -> Optional[Dict]:
        """Get video details using YouTube Data API"""
        if not self.youtube_api:
            return None
        
        try:
            video_response = self.youtube_api.videos().list(
                id=video_id,
                part='snippet,statistics,contentDetails'
            ).execute()
            
            if not video_response.get('items'):
                return None
            
            item = video_response['items'][0]
            snippet = item['snippet']
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            
            return {
                "video_id": video_id,
                "title": snippet.get('title', ''),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "upload_date": snippet.get('publishedAt', ''),
                "view_count": int(statistics.get('viewCount', 0)),
                "like_count": int(statistics.get('likeCount', 0)),
                "description": snippet.get('description', ''),
                "channel_id": snippet.get('channelId', ''),
                "channel_title": snippet.get('channelTitle', ''),
                "thumbnail_url": snippet['thumbnails']['high']['url'] if 'thumbnails' in snippet else '',
                "duration": content_details.get('duration', ''),
                "tags": snippet.get('tags', []),
                "category_id": snippet.get('categoryId', '')
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting API details for video {video_id}: {e}")
            return None
    
    async def extract_all_channel_data(self, max_results: int = 100) -> List[Dict]:
        """Extract data from all configured channels"""
        all_videos = []
        channels = self.channel_manager.get_all_channels()
        
        for channel in channels:
            logger.info(f"🔍 Extracting data from {channel.name}")
            
            # Try yt-dlp first (more reliable for recent videos)
            channel_videos = await self.get_channel_videos_ytdlp(
                channel.handle, max_results
            )
            
            # Fallback to API if yt-dlp fails
            if not channel_videos:
                channel_videos = await self.get_channel_videos_api(
                    channel.channel_id, max_results
                )
            
            all_videos.extend(channel_videos)
            
            # Be respectful to YouTube - add delay between channels
            await asyncio.sleep(1)
        
        logger.info(f"🎉 Total videos extracted: {len(all_videos)}")
        return all_videos