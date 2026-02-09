#!/bin/bash

# SDA Calculator Setup Script

set -e

echo "=================================================="
echo "SDA CALCULATOR SETUP"
echo "=================================================="

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker Desktop."
    exit 1
fi

echo ""
echo "✓ Docker found"

# Create data directory
mkdir -p data

# Check if pricing data exists
if [ ! -f "data/base_prices_complete.csv" ]; then
    echo ""
    echo "⚠️  Pricing data not found!"
    echo "Please copy base_prices_complete.csv to the data/ directory"
    echo ""
    read -p "Press Enter when you've added the file, or Ctrl+C to exit..."
    
    if [ ! -f "data/base_prices_complete.csv" ]; then
        echo "Error: Pricing data still not found. Exiting."
        exit 1
    fi
fi

echo "✓ Pricing data found"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
fi

# Build and start services
echo ""
echo "Building and starting Docker containers..."
docker compose up --build -d

# Wait for database to be ready
echo ""
echo "Waiting for database to be ready..."
sleep 10

# Initialize database
echo ""
echo "Initializing database..."
docker compose exec -T backend python init_db.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✓ SETUP COMPLETE!"
    echo "=================================================="
    echo ""
    echo "Access the application at:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "To stop the application:"
    echo "  docker compose down"
    echo ""
    echo "To view logs:"
    echo "  docker compose logs -f"
    echo ""
else
    echo ""
    echo "Error: Database initialization failed"
    echo "Check logs with: docker compose logs backend"
    exit 1
fi
