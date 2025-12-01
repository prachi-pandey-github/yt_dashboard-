"""
YouTube channel management and configuration
"""
from typing import Dict, List
from dataclasses import dataclass
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import ChannelInfo

@dataclass
class YouTubeChannel:
    """YouTube channel configuration"""
    channel_id: str
    handle: str
    name: str
    description: str
    is_high_frequency: bool = True
    timezone: str = "UTC"

class ChannelManager:
    """Manage YouTube channels to monitor"""
    
    def __init__(self):
        self.channels = self._initialize_channels()
    
    def _initialize_channels(self) -> Dict[str, YouTubeChannel]:
        """Initialize the target channels"""
        return {
            "UCaIGZ2lNpryhA-p9KXr5XNw": YouTubeChannel(
                channel_id="UCaIGZ2lNpryhA-p9KXr5XNw",
                handle="@markets",
                name="Bloomberg Markets",
                description="Bloomberg Television - Global financial news",
                is_high_frequency=True,
                timezone="America/New_York"
            ),
            "UCUDXkpsJIdv1aKb1TCN2p0Q": YouTubeChannel(
                channel_id="UCUDXkpsJIdv1aKb1TCN2p0Q",
                handle="@ANINewsIndia",
                name="ANI News India",
                description="Asian News International - Indian news coverage",
                is_high_frequency=True,
                timezone="Asia/Kolkata"
            ),
            "UCDANGgqLMuoRfpX75LP7bUQ": YouTubeChannel(
                channel_id="UCDANGgqLMuoRfpX75LP7bUQ",
                handle="@testchannel",
                name="Test Channel",
                description="Test channel for system validation",
                is_high_frequency=True,
                timezone="UTC"
            )
        }
    
    def get_channel_by_id(self, channel_id: str) -> YouTubeChannel:
        """Get channel configuration by ID"""
        return self.channels.get(channel_id)
    
    def get_all_channels(self) -> List[YouTubeChannel]:
        """Get all configured channels"""
        return list(self.channels.values())
    
    def get_high_frequency_channels(self) -> List[YouTubeChannel]:
        """Get only high-frequency channels"""
        return [channel for channel in self.channels.values() 
                if channel.is_high_frequency]
    
    def get_channel_handles(self) -> List[str]:
        """Get all channel handles"""
        return [channel.handle for channel in self.channels.values()]
    
    def add_channel(self, channel: YouTubeChannel) -> bool:
        """Add a new channel to monitor"""
        if channel.channel_id in self.channels:
            return False
        
        self.channels[channel.channel_id] = channel
        return True
    
    def to_channel_info(self) -> List[ChannelInfo]:
        """Convert to database ChannelInfo models"""
        return [
            ChannelInfo(
                channel_id=channel.channel_id,
                channel_handle=channel.handle,
                channel_title=channel.name,
                description=channel.description
            )
            for channel in self.channels.values()
        ]