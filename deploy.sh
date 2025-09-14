#!/bin/bash

# Hemogrid Deployment Script
echo "🚀 Starting Hemogrid deployment..."

# Set production settings
export DJANGO_SETTINGS_MODULE=hemogrid.settings_prod

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating superuser..."
python manage.py shell -c "
from accounts.models import User
if not User.objects.filter(email='admin@admin.com').exists():
    User.objects.create_superuser(
        email='admin@admin.com',
        password='12345',
        role='admin',
        is_verified=True
    )
    print('Admin user created successfully!')
else:
    print('Admin user already exists!')
"

# Start Gunicorn server
echo "🌐 Starting Gunicorn server..."
gunicorn --config gunicorn.conf.py hemogrid.wsgi:application

echo "✅ Deployment completed successfully!"
