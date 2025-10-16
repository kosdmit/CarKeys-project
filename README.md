# CarKeys Project

Django-based e-commerce application for car key services.

## Quick Start

### Development
```bash
# Install dependencies
uv sync

# Run migrations
uv run python manage.py migrate

# Start development server
uv run python manage.py runserver
```

### Production Deployment
**See `DEPLOYMENT_STATUS.md` for deployment readiness report**  
**See `DEPLOYMENT.md` for complete deployment guide**  
**See `SSL_SETUP.md` for SSL certificate setup with Let's Encrypt**

```bash
# 1. Create environment file
cp .env.prod.example .env.prod
# Edit .env.prod with your credentials

# 2. Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# 3. Setup SSL certificates (recommended)
./init-letsencrypt.sh

# 4. Create admin user
docker-compose -f docker-compose.prod.yml exec web uv run python manage.py createsuperuser
```

## Project Structure
- `app_landing/` - Landing page application
- `app_ecommerce/` - E-commerce functionality
- `carkeys_project/` - Django project settings
- `nginx/` - Nginx reverse proxy configuration
- `static_files/` - Static assets (CSS, JS, images)
- `templates/` - Django templates

## Documentation
- **DEPLOYMENT_STATUS.md** - Current deployment readiness
- **DEPLOYMENT.md** - Complete deployment guide
- **SSL_SETUP.md** - SSL certificate setup with automatic renewal
- **.env.prod.example** - Environment variables template

## Tech Stack
- Django 4.2.2
- Python 3.12
- PostgreSQL 15
- Nginx
- Gunicorn
- Docker & Docker Compose
- Let's Encrypt / Certbot (SSL)
