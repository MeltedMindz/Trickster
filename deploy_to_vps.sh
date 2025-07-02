#!/bin/bash
set -e

VPS_HOST="root@5.78.71.231"
REPO_URL="git@github.com:MeltedMindz/Trickster.git"

echo "🚀 Deploying AI Religion Architects to VPS..."

# Check if we can connect to VPS
echo "🔌 Testing VPS connection..."
ssh -o ConnectTimeout=10 $VPS_HOST "echo 'VPS connection successful'"

# Deploy commands
echo "📦 Deploying application..."
ssh $VPS_HOST << 'ENDSSH'
    # Update system
    apt update

    # Install Docker if not present
    if ! command -v docker &> /dev/null; then
        echo "🐳 Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
    fi

    # Install Docker Compose if not present
    if ! command -v docker-compose &> /dev/null; then
        echo "🐙 Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi

    # Setup firewall
    echo "🔥 Configuring firewall..."
    ufw allow 22
    ufw allow 8000
    ufw --force enable

    # Clone or update repository
    if [ -d "Trickster" ]; then
        echo "📁 Updating existing repository..."
        cd Trickster
        git pull origin main
    else
        echo "📥 Cloning repository..."
        git clone git@github.com:MeltedMindz/Trickster.git
        cd Trickster
    fi

    # Setup environment file
    if [ ! -f ".env" ]; then
        echo "⚙️ Creating .env file..."
        cp .env.example .env
        echo "❌ IMPORTANT: You need to manually edit .env with your Claude API key!"
        echo "Run: nano .env and update CLAUDE_API_KEY"
    fi

    # Stop existing containers
    echo "🛑 Stopping existing containers..."
    docker-compose down || true

    # Build and start
    echo "🚀 Starting AI Religion Architects..."
    docker-compose up -d --build

    # Show status
    echo "📊 Container status:"
    docker-compose ps

    echo "✅ Deployment complete!"
    echo "🌐 Access the web interface at: http://5.78.71.231:8000"
    echo "⚠️  Don't forget to update your .env file with a new Claude API key!"
ENDSSH

echo "✨ Deployment script completed!"
echo "🔑 Next steps:"
echo "1. SSH to your VPS: ssh root@5.78.71.231"
echo "2. Edit the .env file: cd Trickster && nano .env"
echo "3. Add your NEW Claude API key (rotate the old one first!)"
echo "4. Restart the container: docker-compose restart"
echo "5. Visit: http://5.78.71.231:8000"