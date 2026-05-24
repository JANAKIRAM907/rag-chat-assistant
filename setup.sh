#!/bin/bash

# GenAI Chat Assistant with RAG - Quick Setup Script
# Run this script to setup the project

set -e

echo "=================================="
echo "RAG Chat Assistant Setup"
echo "=================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "✓ Creating virtual environment..."
    python3 -m venv venv
else
    echo ""
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "✓ Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "✓ Installing dependencies..."
echo "  This may take a few minutes..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "✓ Creating .env file..."
    cp .env.example .env
    echo "  Please edit .env and add your ANTHROPIC_API_KEY"
else
    echo "✓ .env file already exists"
fi

# Verify setup
echo ""
echo "=================================="
echo "Setup Complete! ✓"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env and add your Claude API key:"
echo "   ANTHROPIC_API_KEY=sk_test_..."
echo ""
echo "2. Run the application:"
echo "   python -m main"
echo ""
echo "3. Open browser:"
echo "   http://localhost:8000"
echo ""
echo "For deployment, see DEPLOYMENT.md"
echo ""
