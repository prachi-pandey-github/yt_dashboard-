"""
WebSub (PubSubHubbub) handler for real-time YouTube notifications
No AWS dependencies
"""
import asyncio
import aiohttp
from typing import Dict, Optional
import logging
from urllib.parse import urlencode
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import get_settings
from youtube.channel_manager import ChannelManager

logger = logging.getLogger(__name__)

class WebSubHandler:
    """Handle WebSub subscriptions for YouTube channels"""
    
    def __init__(self):
        self.settings = get_settings()
        self.channel_manager = ChannelManager()
        self.callback_url = f"{self.settings.webhook_base_url}/webhook/youtube"
    
    async def subscribe_to_channel(self, channel_id: str) -> bool:
        """Subscribe to a YouTube channel using WebSub"""
        hub_url = "https://pubsubhubbub.appspot.com/subscribe"
        
        data = {
            'hub.callback': self.callback_url,
            'hub.topic': f'https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}',
            'hub.verify': 'async',
            'hub.mode': 'subscribe',
            'hub.verify_token': self.settings.webhook_verify_token,
            'hub.secret': self.settings.webhook_secret,
            'hub.lease_seconds': '864000'  # 10 days
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(hub_url, data=data) as response:
                    if response.status in [202, 204]:
                        logger.info(f"✅ Successfully subscribed to channel: {channel_id}")
                        return True
                    else:
                        text = await response.text()
                        logger.error(f"❌ Subscription failed for {channel_id}: {response.status} - {text}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Error subscribing to channel {channel_id}: {e}")
            return False
    
    async def unsubscribe_from_channel(self, channel_id: str) -> bool:
        """Unsubscribe from a YouTube channel"""
        hub_url = "https://pubsubhubbub.appspot.com/subscribe"
        
        data = {
            'hub.callback': self.callback_url,
            'hub.topic': f'https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}',
            'hub.mode': 'unsubscribe',
            'hub.verify_token': self.settings.webhook_verify_token,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(hub_url, data=data) as response:
                    if response.status in [202, 204]:
                        logger.info(f"✅ Successfully unsubscribed from channel: {channel_id}")
                        return True
                    else:
                        logger.error(f"❌ Unsubscription failed for {channel_id}: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Error unsubscribing from channel {channel_id}: {e}")
            return False
    
    async def subscribe_to_all_channels(self) -> Dict[str, bool]:
        """Subscribe to all configured channels"""
        results = {}
        channels = self.channel_manager.get_all_channels()
        
        for channel in channels:
            success = await self.subscribe_to_channel(channel.channel_id)
            results[channel.channel_id] = success
            
            # Add delay between subscriptions to be respectful
            await asyncio.sleep(1)
        
        successful = sum(results.values())
        total = len(results)
        logger.info(f"🎯 Subscription results: {successful}/{total} successful")
        
        return results
    
    async def renew_subscriptions(self):
        """Renew all subscriptions (should be called periodically)"""
        logger.info("🔄 Renewing WebSub subscriptions...")
        return await self.subscribe_to_all_channels()
    
    def parse_atom_feed(self, feed_content: str) -> Optional[Dict]:
        """Parse Atom feed from YouTube notification"""
        try:
            # Simple Atom feed parsing
            if '<entry>' in feed_content and '<yt:videoId>' in feed_content:
                import re
                
                # Extract video ID
                video_id_match = re.search(r'<yt:videoId>(.*?)</yt:videoId>', feed_content)
                video_id = video_id_match.group(1) if video_id_match else None
                
                # Extract channel ID
                channel_id_match = re.search(r'<yt:channelId>(.*?)</yt:channelId>', feed_content)
                channel_id = channel_id_match.group(1) if channel_id_match else None
                
                # Extract title
                title_match = re.search(r'<title>(.*?)</title>', feed_content)
                title = title_match.group(1) if title_match else None
                
                if video_id and channel_id:
                    return {
                        'video_id': video_id,
                        'channel_id': channel_id,
                        'title': title,
                        'video_url': f'https://www.youtube.com/watch?v={video_id}'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error parsing Atom feed: {e}")
            return None