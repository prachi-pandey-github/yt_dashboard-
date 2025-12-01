"""
Webhook handler for YouTube notifications - No AWS dependencies
"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Header
from pydantic import BaseModel
import hmac
import hashlib
import logging
from typing import Optional

from src.youtube.websub_handler import WebSubHandler
from src.youtube.data_extractor import YouTubeDataExtractor
from src.database.mongodb_client import MongoDBClient
from src.database.models import VideoMetadata
from src.utils.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])

# Initialize handlers
websub_handler = WebSubHandler()
youtube_extractor = YouTubeDataExtractor()
db_client = MongoDBClient()

class WebhookVerification(BaseModel):
    hub_mode: str
    hub_challenge: Optional[str] = None
    hub_topic: Optional[str] = None
    hub_lease_seconds: Optional[int] = None

@router.get("/youtube")
async def youtube_webhook_verification(request: Request):
    """Handle YouTube WebSub verification"""
    params = dict(request.query_params)
    logger.info(f"🔔 Webhook verification request: {params}")
    
    hub_mode = params.get('hub.mode')
    hub_challenge = params.get('hub.challenge')
    hub_verify_token = params.get('hub.verify_token')
    
    settings = get_settings()
    
    if hub_mode == 'subscribe':
        if hub_verify_token != settings.webhook_verify_token:
            logger.warning(f"❌ Verification token mismatch: {hub_verify_token}")
            raise HTTPException(status_code=403, detail="Verification token mismatch")
        
        logger.info("✅ Webhook verification successful")
        return int(hub_challenge)
    
    elif hub_mode == 'unsubscribe':
        logger.info("📤 Webhook unsubscription request")
        return "Unsubscribed"
    
    raise HTTPException(status_code=400, detail="Invalid request mode")

@router.post("/youtube")
async def youtube_webhook_notification(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature: Optional[str] = Header(None)
):
    """Handle YouTube notification - real-time video publishing"""
    body = await request.body()
    body_text = body.decode()
    
    logger.info("🎬 Received YouTube notification")
    
    # Verify signature if secret is provided
    settings = get_settings()
    if settings.webhook_secret and x_hub_signature:
        signature = x_hub_signature.replace('sha1=', '')
        expected_signature = hmac.new(
            settings.webhook_secret.encode(), 
            body, 
            hashlib.sha1
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning("❌ Invalid webhook signature")
            raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Process notification in background
    background_tasks.add_task(process_youtube_notification, body_text)
    
    return {"status": "processing", "message": "Notification received"}

async def process_youtube_notification(notification_body: str):
    """Process YouTube notification and extract video data"""
    try:
        logger.info("🔍 Processing YouTube notification...")
        
        # Parse Atom feed to get video information
        video_info = websub_handler.parse_atom_feed(notification_body)
        
        if not video_info:
            logger.warning("⚠️ Could not parse video information from notification")
            return
        
        video_id = video_info['video_id']
        channel_id = video_info['channel_id']
        
        logger.info(f"📹 New video detected: {video_id} from channel: {channel_id}")
        
        # Check if video already exists (idempotency)
        existing_video = db_client.collection.find_one({"video_id": video_id})
        if existing_video:
            logger.info(f"⚠️ Video {video_id} already exists in database")
            return
        
        # Get detailed video information
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_data = await youtube_extractor.get_video_details(video_url)
        
        if not video_data:
            logger.error(f"❌ Could not fetch details for video {video_id}")
            return
        
        # Convert to VideoMetadata model
        video_metadata = VideoMetadata(**video_data)
        
        # Store in database
        success = db_client.insert_video(video_metadata)
        
        if success:
            logger.info(f"✅ Successfully processed and stored video: {video_data['title']}")
        else:
            logger.error(f"❌ Failed to store video: {video_data['title']}")
    
    except Exception as e:
        logger.error(f"❌ Error processing notification: {e}")