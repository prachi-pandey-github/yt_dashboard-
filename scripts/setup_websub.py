"""
WebSub subscription setup script - No AWS dependencies
"""
import asyncio
import logging
from src.youtube.websub_handler import WebSubHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Setup WebSub subscriptions for all channels"""
    logger.info("🔔 Setting up WebSub subscriptions...")
    
    websub_handler = WebSubHandler()
    
    # Subscribe to all channels
    results = await websub_handler.subscribe_to_all_channels()
    
    # Display results
    successful = sum(results.values())
    total = len(results)
    
    logger.info(f"🎯 Subscription summary: {successful}/{total} successful")
    
    for channel_id, success in results.items():
        status = "✅" if success else "❌"
        logger.info(f"{status} {channel_id}")

if __name__ == "__main__":
    asyncio.run(main())