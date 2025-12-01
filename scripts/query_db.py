"""
Database query script for testing - No AWS dependencies
"""
import argparse
import json
import sys
import os
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.mongodb_client import MongoDBClient
from src.youtube.channel_manager import ChannelManager

def main():
    """Query database and display results"""
    parser = argparse.ArgumentParser(description="Query YouTube videos database")
    parser.add_argument("--recent", type=int, default=5, help="Number of recent videos to show")
    parser.add_argument("--channel", type=str, help="Filter by channel ID")
    parser.add_argument("--search", type=str, help="Search query")
    parser.add_argument("--stats", action="store_true", help="Show channel statistics")
    
    args = parser.parse_args()
    
    db_client = MongoDBClient()
    channel_manager = ChannelManager()
    
    print("📊 YouTube Database Query Tool")
    print("=" * 50)
    
    if args.stats:
        # Show channel statistics
        channels = channel_manager.get_all_channels()
        for channel in channels:
            count = db_client.get_video_count_by_channel(channel.channel_id)
            stats = db_client.get_channel_stats(channel.channel_id)
            print(f"\n📺 {channel.name} ({channel.channel_id})")
            print(f"   Total Videos: {count}")
            if stats:
                print(f"   Total Views: {stats.get('total_views', 0):,}")
                print(f"   Average Views: {stats.get('average_views', 0):,.0f}")
    
    elif args.search:
        # Search videos
        results = db_client.search_videos(args.search, args.channel)
        print(f"\n🔍 Search Results for '{args.search}': {len(results)} videos")
        for video in results[:args.recent]:
            print(f"\n📹 {video['title']}")
            print(f"   📅 {video['upload_date']}")
            print(f"   👀 {video.get('view_count', 0)} views")
            print(f"   🔗 {video['url']}")
    
    else:
        # Show recent videos
        videos = db_client.get_recent_videos(args.recent, args.channel)
        channel_info = f" from channel {args.channel}" if args.channel else ""
        print(f"\n🆕 Most recent {args.recent} videos{channel_info}:")
        
        for i, video in enumerate(videos, 1):
            print(f"\n{i}. 📹 {video['title']}")
            print(f"   🏷️  Channel: {video.get('channel_title', 'N/A')}")
            print(f"   📅 Uploaded: {video['upload_date']}")
            print(f"   👀 Views: {video.get('view_count', 0):,}")
            print(f"   👍 Likes: {video.get('like_count', 0):,}")
            print(f"   🔗 URL: {video['url']}")

if __name__ == "__main__":
    main()