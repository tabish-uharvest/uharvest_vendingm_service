#!/bin/bash
# Urban Harvest Vending Machine API Setup Script
# This script sets up the development environment for the FastAPI service

echo "========================================"
echo "Urban Harvest Vending Machine API Setup"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

echo "Step 1: Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "Step 2: Activating virtual environment..."
source venv/bin/activate

echo "Step 3: Upgrading pip..."
python -m pip install --upgrade pip

echo "Step 4: Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "Step 5: Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Environment file created from template."
    echo "IMPORTANT: Please edit .env file with your database credentials!"
else
    echo "Environment file already exists."
fi

echo
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Edit .env file with your database credentials"
echo "2. Create PostgreSQL database: createdb uharvest_vending"
echo "3. Import schema: psql -d uharvest_vending -f ../database/schema.sql"
echo "4. Start server: python run_server.py --reload --debug"
echo
echo "API will be available at:"
echo "- Base URL: http://localhost:8000"
echo "- Documentation: http://localhost:8000/docs"
echo "- Health Check: http://localhost:8000/api/v1/health"
echo
