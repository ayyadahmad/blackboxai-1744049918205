# Social Media Automation Platform

A Flask-based social media automation platform for scheduling and managing posts across multiple social media platforms with AI-powered caption generation.

## Features

- **Multi-Platform Support**: Facebook, Twitter, Instagram, Pinterest, TikTok
- **Media Management**: Upload and auto-resize photos and videos
- **Smart Scheduling**: Schedule posts with cron job support
- **AI Captions**: Generate captions using Hugging Face transformers
- **Secure**: API token encryption, user authentication, rate limiting

## Requirements

- Python 3.6+
- MySQL Database
- Required packages in requirements.txt

## Quick Start

1. **Setup Environment**
```bash
# Clone repository
git clone https://github.com/yourusername/social-media-automation.git
cd social-media-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings:
# - SECRET_KEY
# - DATABASE_URI
# - Social Media API tokens
```

3. **Initialize Database**
```bash
flask db init
flask db migrate
flask db upgrade
```

4. **Run Application**
```bash
python app.py
# Access at http://localhost:8000
```

## Configuration Guide

### Database Setup
1. Create MySQL database
2. Update DATABASE_URI in .env
3. Run migrations

### Platform Setup

#### Facebook
- Create Developer account
- Create Facebook App
- Get Page Access Token
- Add to settings

#### Twitter
- Get Developer account
- Create Twitter App
- Generate API tokens
- Add to settings

#### Instagram
- Setup Instagram Graph API
- Get access token
- Add to settings

#### Pinterest
- Get Developer account
- Create app & get token
- Add to settings

#### TikTok
- Join TikTok Developers
- Get API credentials
- Add to settings

## Project Structure
```
social-media-automation/
├── app.py              # Main application
├── config.py           # Configuration
├── models.py           # Database models
├── forms.py            # Form definitions
├── scheduler.py        # Scheduling logic
├── social_media.py     # Platform integrations
├── static/            
│   ├── css/           # Stylesheets
│   └── js/            # JavaScript
├── templates/          # HTML templates
├── requirements.txt    
└── .env               
```

## Usage

1. Register/Login to account
2. Configure platform settings
3. Create new post:
   - Select platform(s)
   - Upload media
   - Write/generate caption
   - Set schedule
   - Submit

## Security

- Encrypted API tokens
- Hashed passwords
- Rate limiting
- CSRF protection
- Secure sessions

## Troubleshooting

### Common Issues

1. **Database Errors**
   - Check credentials
   - Verify MySQL running
   - Check permissions

2. **API Errors**
   - Verify tokens
   - Check expiration
   - Review permissions

3. **Scheduler Issues**
   - Check cron setup
   - Verify timezone
   - Review logs

## License

MIT License - See LICENSE file

## Acknowledgments

- Flask framework
- Bootstrap UI
- Font Awesome
- Hugging Face