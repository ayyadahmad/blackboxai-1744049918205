import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import and_

from models import db, Post, PostLog
from social_media import SocialMediaManager
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PostScheduler:
    """Handle scheduling and processing of social media posts."""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app context."""
        self.app = app
        self.social_media_manager = SocialMediaManager(app.config)
    
    def get_pending_posts(self) -> List[Post]:
        """Get all pending posts that are due for posting."""
        try:
            current_time = datetime.utcnow()
            return Post.query.filter(
                and_(
                    Post.status == 'pending',
                    Post.scheduled_time <= current_time,
                    Post.retry_count < 3  # Max retry attempts
                )
            ).all()
        except Exception as e:
            logger.error(f"Error fetching pending posts: {str(e)}")
            return []
    
    def process_post(self, post: Post) -> bool:
        """Process a single post."""
        try:
            # Update post status to processing
            post.status = 'processing'
            db.session.commit()
            
            # Attempt to post to social media
            result = self.social_media_manager.post(
                platform=post.platform,
                media_path=post.media_url,
                caption=post.caption
            )
            
            # Create log entry
            log = PostLog(
                post_id=post.id,
                attempt_number=post.retry_count + 1,
                status='success' if result['success'] else 'failed',
                response_data=str(result),
                error_message=result.get('error')
            )
            db.session.add(log)
            
            if result['success']:
                post.status = 'completed'
                logger.info(f"Successfully posted to {post.platform}. Post ID: {post.id}")
            else:
                post.status = 'failed'
                post.error_message = result.get('error')
                post.retry_count += 1
                
                # If max retries reached, mark as permanently failed
                if post.retry_count >= 3:
                    post.status = 'failed_permanent'
                    logger.error(f"Post {post.id} permanently failed after max retries")
                else:
                    # Schedule retry after exponential backoff
                    retry_delay = 2 ** post.retry_count  # exponential backoff
                    post.scheduled_time = datetime.utcnow() + timedelta(minutes=retry_delay)
                    logger.warning(f"Post {post.id} failed, scheduled retry in {retry_delay} minutes")
            
            db.session.commit()
            return result['success']
            
        except Exception as e:
            logger.error(f"Error processing post {post.id}: {str(e)}")
            post.status = 'failed'
            post.error_message = str(e)
            post.retry_count += 1
            db.session.commit()
            return False
    
    def process_pending_posts(self) -> Dict[str, Any]:
        """Process all pending posts."""
        results = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            pending_posts = self.get_pending_posts()
            results['total'] = len(pending_posts)
            
            for post in pending_posts:
                try:
                    success = self.process_post(post)
                    if success:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Post {post.id} failed: {post.error_message}")
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Post {post.id} failed with exception: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in process_pending_posts: {str(e)}")
            results['errors'].append(f"Global error: {str(e)}")
            return results
    
    def retry_failed_post(self, post_id: int) -> Dict[str, Any]:
        """Manually retry a failed post."""
        try:
            post = Post.query.get(post_id)
            if not post:
                return {'success': False, 'error': 'Post not found'}
            
            if post.status not in ['failed', 'failed_permanent']:
                return {'success': False, 'error': 'Post is not in failed status'}
            
            # Reset retry count and status
            post.retry_count = 0
            post.status = 'pending'
            post.scheduled_time = datetime.utcnow()
            db.session.commit()
            
            # Process the post immediately
            success = self.process_post(post)
            return {
                'success': success,
                'message': 'Post processed successfully' if success else 'Post processing failed',
                'post_id': post_id
            }
            
        except Exception as e:
            logger.error(f"Error retrying post {post_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def cleanup_old_posts(self, days: int = 30) -> Dict[str, Any]:
        """Clean up old completed posts."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            old_posts = Post.query.filter(
                and_(
                    Post.status == 'completed',
                    Post.created_at <= cutoff_date
                )
            ).all()
            
            for post in old_posts:
                # Delete associated media files
                if post.media_url and os.path.exists(post.media_url):
                    os.remove(post.media_url)
                
                # Delete post and its logs
                db.session.delete(post)
            
            db.session.commit()
            return {
                'success': True,
                'posts_cleaned': len(old_posts)
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old posts: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

def run_scheduler():
    """Entry point for cron job."""
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            scheduler = PostScheduler(app)
            results = scheduler.process_pending_posts()
            
            # Log results
            logger.info(f"Scheduler run completed: {results}")
            
            # Clean up old posts (30 days)
            cleanup_results = scheduler.cleanup_old_posts(30)
            logger.info(f"Cleanup completed: {cleanup_results}")
            
    except Exception as e:
        logger.error(f"Error running scheduler: {str(e)}")

if __name__ == '__main__':
    run_scheduler()