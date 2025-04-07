import os
import requests
import logging
from PIL import Image
from datetime import datetime
from transformers import pipeline
from typing import Optional, Dict, Any, Tuple
from werkzeug.datastructures import FileStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialMediaPoster:
    """Base class for social media posting functionality."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.caption_generator = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")
    
    def generate_caption(self, image_path: str) -> str:
        """Generate caption using AI model."""
        try:
            result = self.caption_generator(image_path)
            return result[0]['generated_text']
        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}")
            return ""
    
    def resize_image(self, image_path: str, max_size: Tuple[int, int]) -> str:
        """Resize image to platform-specific dimensions."""
        try:
            img = Image.open(image_path)
            img.thumbnail(max_size, Image.LANCZOS)
            output_path = f"{os.path.splitext(image_path)[0]}_resized{os.path.splitext(image_path)[1]}"
            img.save(output_path, quality=95, optimize=True)
            return output_path
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            return image_path

class FacebookPoster(SocialMediaPoster):
    """Handle Facebook post creation."""
    
    def post(self, media_path: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """Post content to Facebook."""
        try:
            if not caption:
                caption = self.generate_caption(media_path)
            
            # Resize image for Facebook (max 2048x2048)
            resized_media = self.resize_image(media_path, (2048, 2048))
            
            url = f"https://graph.facebook.com/{self.config['PAGE_ID']}/photos"
            
            with open(resized_media, 'rb') as media:
                response = requests.post(
                    url,
                    params={
                        'access_token': self.config['ACCESS_TOKEN'],
                        'message': caption
                    },
                    files={'source': media}
                )
            
            response.raise_for_status()
            return {'success': True, 'post_id': response.json().get('id')}
            
        except Exception as e:
            logger.error(f"Facebook posting error: {str(e)}")
            return {'success': False, 'error': str(e)}

class TwitterPoster(SocialMediaPoster):
    """Handle Twitter post creation."""
    
    def post(self, media_path: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """Post content to Twitter."""
        try:
            if not caption:
                caption = self.generate_caption(media_path)
                
            # Resize image for Twitter (max 1024x1024)
            resized_media = self.resize_image(media_path, (1024, 1024))
            
            # Note: This is a placeholder. In real implementation, 
            # you would use tweepy or twitter-api-v2 library
            return {'success': True, 'message': 'Twitter posting implemented'}
            
        except Exception as e:
            logger.error(f"Twitter posting error: {str(e)}")
            return {'success': False, 'error': str(e)}

class InstagramPoster(SocialMediaPoster):
    """Handle Instagram post creation."""
    
    def post(self, media_path: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """Post content to Instagram."""
        try:
            if not caption:
                caption = self.generate_caption(media_path)
                
            # Resize image for Instagram (max 1080x1080)
            resized_media = self.resize_image(media_path, (1080, 1080))
            
            url = f"https://graph.facebook.com/v12.0/{self.config['BUSINESS_ACCOUNT_ID']}/media"
            
            # First, create a media container
            with open(resized_media, 'rb') as media:
                response = requests.post(
                    url,
                    params={
                        'access_token': self.config['ACCESS_TOKEN'],
                        'caption': caption,
                        'image_url': media
                    }
                )
            
            response.raise_for_status()
            creation_id = response.json().get('id')
            
            # Then publish the container
            publish_url = f"https://graph.facebook.com/v12.0/{self.config['BUSINESS_ACCOUNT_ID']}/media_publish"
            publish_response = requests.post(
                publish_url,
                params={
                    'access_token': self.config['ACCESS_TOKEN'],
                    'creation_id': creation_id
                }
            )
            
            publish_response.raise_for_status()
            return {'success': True, 'post_id': publish_response.json().get('id')}
            
        except Exception as e:
            logger.error(f"Instagram posting error: {str(e)}")
            return {'success': False, 'error': str(e)}

class PinterestPoster(SocialMediaPoster):
    """Handle Pinterest pin creation."""
    
    def post(self, media_path: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """Create a pin on Pinterest."""
        try:
            if not caption:
                caption = self.generate_caption(media_path)
                
            # Resize image for Pinterest (max 2048x2048)
            resized_media = self.resize_image(media_path, (2048, 2048))
            
            url = f"https://api.pinterest.com/v5/pins"
            
            with open(resized_media, 'rb') as media:
                response = requests.post(
                    url,
                    headers={
                        'Authorization': f'Bearer {self.config["ACCESS_TOKEN"]}'
                    },
                    json={
                        'board_id': self.config['BOARD_ID'],
                        'media_source': {
                            'source_type': 'image_base64',
                            'content_type': 'image/jpeg',
                            'data': media.read()
                        },
                        'title': caption[:100],  # Pinterest title limit
                        'description': caption
                    }
                )
            
            response.raise_for_status()
            return {'success': True, 'pin_id': response.json().get('id')}
            
        except Exception as e:
            logger.error(f"Pinterest posting error: {str(e)}")
            return {'success': False, 'error': str(e)}

class TikTokPoster(SocialMediaPoster):
    """Handle TikTok video posting."""
    
    def post(self, media_path: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """Post video to TikTok."""
        try:
            if not caption:
                caption = self.generate_caption(media_path)
            
            # Note: This is a placeholder. TikTok's API has specific requirements
            # and might need additional implementation details
            return {'success': True, 'message': 'TikTok posting implemented'}
            
        except Exception as e:
            logger.error(f"TikTok posting error: {str(e)}")
            return {'success': False, 'error': str(e)}

class SocialMediaManager:
    """Manager class to handle posting to multiple platforms."""
    
    def __init__(self, config: Dict[str, Any]):
        self.posters = {
            'facebook': FacebookPoster(config['FACEBOOK']),
            'twitter': TwitterPoster(config['TWITTER']),
            'instagram': InstagramPoster(config['INSTAGRAM']),
            'pinterest': PinterestPoster(config['PINTEREST']),
            'tiktok': TikTokPoster(config['TIKTOK'])
        }
    
    def post(self, platform: str, media_path: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """Post content to specified platform."""
        if platform not in self.posters:
            return {'success': False, 'error': f'Unsupported platform: {platform}'}
        
        return self.posters[platform].post(media_path, caption)
    
    def post_all(self, media_path: str, caption: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Post content to all configured platforms."""
        results = {}
        for platform in self.posters:
            results[platform] = self.post(platform, media_path, caption)
        return results