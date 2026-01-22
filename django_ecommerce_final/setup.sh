#!/bin/bash
# Setup Script for Django E-Commerce Platform

echo "========================================="
echo "Django E-Commerce Setup Script"
echo "========================================="

# Step 1: Install dependencies
echo ""
echo "Step 1: Installing dependencies..."
pip install -r requirements.txt

# Step 2: Run migrations
echo ""
echo "Step 2: Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Step 3: Create superuser
echo ""
echo "Step 3: Creating superuser..."
echo "Please enter superuser details:"
python manage.py createsuperuser

# Step 4: Create demo products (optional)
echo ""
echo "Step 4: Creating demo products..."
python manage.py create_demo_products

# Step 5: Collect static files
echo ""
echo "Step 5: Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To start the development server, run:"
echo "python manage.py runserver"
echo ""
echo "Then visit: http://localhost:8000"
echo ""
echo "Admin Panel: http://localhost:8000/admin"
echo ""
