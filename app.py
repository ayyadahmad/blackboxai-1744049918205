import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import config
from models import db, User, Post, Settings, PostLog
from forms import (LoginForm, RegistrationForm, PostForm, SettingsForm, 
                  RetryPostForm, DeletePostForm, GenerateCaptionForm)
from social_media import SocialMediaManager
from scheduler import PostScheduler

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Initialize social media manager and scheduler
    social_media_manager = SocialMediaManager(app.config)
    scheduler = PostScheduler(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Authentication routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            flash('Invalid username or password', 'error')
        
        return render_template('login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already exists', 'error')
                return render_template('register.html', form=form)
            
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))
    
    # Main application routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get user's posts with pagination
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(user_id=current_user.id)\
            .order_by(Post.scheduled_time.desc())\
            .paginate(page=page, per_page=10)
        
        return render_template('dashboard.html', posts=posts)
    
    @app.route('/post/new', methods=['GET', 'POST'])
    @login_required
    def new_post():
        form = PostForm()
        if form.validate_on_submit():
            try:
                # Save uploaded media
                media = form.media.data
                filename = secure_filename(media.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                media.save(filepath)
                
                # Create post
                post = Post(
                    user_id=current_user.id,
                    platform=form.platform.data,
                    media_type='video' if filename.lower().endswith(('.mp4', '.mov')) else 'photo',
                    media_url=filepath,
                    caption=form.caption.data,
                    scheduled_time=form.scheduled_time.data
                )
                
                db.session.add(post)
                db.session.commit()
                
                flash('Post scheduled successfully!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                flash(f'Error scheduling post: {str(e)}', 'error')
        
        return render_template('post_form.html', form=form)
    
    @app.route('/settings', methods=['GET', 'POST'])
    @login_required
    def settings():
        form = SettingsForm()
        if form.validate_on_submit():
            try:
                # Update settings for each platform
                platforms = {
                    'facebook': ['access_token', 'page_id'],
                    'twitter': ['api_key', 'api_secret', 'access_token', 'access_token_secret'],
                    'instagram': ['access_token', 'business_account_id'],
                    'pinterest': ['access_token', 'board_id'],
                    'tiktok': ['access_token', 'open_id']
                }
                
                for platform, keys in platforms.items():
                    for key in keys:
                        setting_key = f"{platform}_{key}"
                        setting_value = getattr(form, setting_key).data
                        
                        if setting_value:
                            setting = Settings.query.filter_by(
                                user_id=current_user.id,
                                platform=platform,
                                key_name=key
                            ).first()
                            
                            if setting:
                                setting.key_value = setting_value
                            else:
                                setting = Settings(
                                    user_id=current_user.id,
                                    platform=platform,
                                    key_name=key,
                                    key_value=setting_value
                                )
                                db.session.add(setting)
                
                db.session.commit()
                flash('Settings updated successfully!', 'success')
                
            except Exception as e:
                flash(f'Error updating settings: {str(e)}', 'error')
        else:
            # Load current settings
            settings = Settings.query.filter_by(user_id=current_user.id).all()
            for setting in settings:
                field_name = f"{setting.platform}_{setting.key_name}"
                if hasattr(form, field_name):
                    field = getattr(form, field_name)
                    field.data = setting.key_value
        
        return render_template('settings.html', form=form)
    
    @app.route('/post/<int:post_id>/retry', methods=['POST'])
    @login_required
    def retry_post(post_id):
        post = Post.query.get_or_404(post_id)
        if post.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        result = scheduler.retry_failed_post(post_id)
        return jsonify(result)
    
    @app.route('/post/<int:post_id>/delete', methods=['POST'])
    @login_required
    def delete_post(post_id):
        post = Post.query.get_or_404(post_id)
        if post.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        try:
            # Delete associated media file
            if post.media_url and os.path.exists(post.media_url):
                os.remove(post.media_url)
            
            db.session.delete(post)
            db.session.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/generate-caption', methods=['POST'])
    @login_required
    @limiter.limit("10 per hour")  # Limit AI caption generation
    def generate_caption():
        form = GenerateCaptionForm()
        if form.validate_on_submit():
            try:
                media = form.image.data
                filename = secure_filename(media.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'temp', filename)
                media.save(filepath)
                
                # Generate caption using the social media manager
                caption = social_media_manager.posters[form.platform.data].generate_caption(filepath)
                
                # Clean up temporary file
                os.remove(filepath)
                
                return jsonify({'success': True, 'caption': caption})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        return jsonify({'success': False, 'error': 'Invalid form data'})
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000)