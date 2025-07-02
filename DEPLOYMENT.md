# AI Religion Architects - Deployment Guide

This guide covers deploying the AI Religion Architects system for perpetual, real-time operation.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Vercel        │    │   VPS/Cloud      │    │   Users         │
│   Frontend      │◄───┤   Docker Stack   │◄───┤   Browsers      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │
                       ┌───────┴────────┐
                       │                │
               ┌───────▼──────┐ ┌──────▼─────────┐
               │  WebSocket   │ │  AI Religion   │
               │  Server      │ │  Orchestrator  │
               │  (FastAPI)   │ │  (Python)      │
               └──────────────┘ └────────────────┘
                       │
               ┌───────▼──────┐
               │   SQLite     │
               │   Database   │
               └──────────────┘
```

## Prerequisites

1. **VPS/Cloud Server** (DigitalOcean, AWS, etc.)
   - Ubuntu 20.04+ or similar
   - 2GB+ RAM recommended
   - Docker and Docker Compose installed

2. **GitHub Repository**
   - Fork or create new repository with this code
   - Enable GitHub Actions

3. **Vercel Account**
   - Connected to your GitHub repository

## Step 1: VPS Setup

### 1.1 Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login to apply group changes
```

### 1.2 Set up deployment directory

```bash
sudo mkdir -p /opt/ai-religion-architects
sudo chown $USER:$USER /opt/ai-religion-architects
cd /opt/ai-religion-architects

# Create necessary directories
mkdir -p data logs nginx/ssl
```

### 1.3 Configure firewall

```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## Step 2: GitHub Repository Setup

### 2.1 Repository Secrets

Add these secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

- `VPS_HOST`: Your VPS IP address
- `VPS_USERNAME`: Your VPS username (usually `root` or `ubuntu`)
- `VPS_SSH_KEY`: Your private SSH key (generate with `ssh-keygen`)

### 2.2 SSH Key Setup

On your VPS:
```bash
# Generate SSH key if you don't have one
ssh-keygen -t rsa -b 4096 -C "github-actions"

# Add public key to authorized_keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# Display private key for GitHub secret
cat ~/.ssh/id_rsa
```

## Step 3: VPS Deployment

### 3.1 Clone and deploy

```bash
cd /opt/ai-religion-architects

# Clone your repository
git clone https://github.com/yourusername/ai-religion-architects.git .

# Copy environment file
cp docker-compose.yml docker-compose.production.yml

# Start the services
docker-compose -f docker-compose.production.yml up -d

# Check logs
docker-compose -f docker-compose.production.yml logs -f
```

### 3.2 SSL Certificate (Optional but recommended)

```bash
# Install Certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/

# Update nginx config for HTTPS
# Edit nginx/nginx.conf to add SSL configuration
```

## Step 4: Vercel Frontend Deployment

### 4.1 Connect to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Import your repository
4. Configure build settings:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: `echo "Static build"`
   - **Output Directory**: `.`

### 4.2 Environment Variables

In Vercel dashboard, add environment variables:
- `WS_URL`: `wss://your-domain.com/ws`
- `API_URL`: `https://your-domain.com/api`

### 4.3 Update Configuration

Edit `frontend/_config.js` and update the production URLs:

```javascript
production: {
  WS_URL: 'wss://your-actual-domain.com/ws',
  API_URL: 'https://your-actual-domain.com/api'
}
```

## Step 5: Monitoring and Maintenance

### 5.1 Health Checks

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f ai-religion-architects

# Check WebSocket connection
curl -f http://localhost:8000/

# Monitor database size
ls -lh data/religion_memory.db
```

### 5.2 Database Backups

```bash
# Create backup script
cat > /opt/ai-religion-architects/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /opt/ai-religion-architects/data/religion_memory.db \
   /opt/ai-religion-architects/data/religion_memory_backup_$DATE.db
# Keep only last 7 backups
cd /opt/ai-religion-architects/data
ls -t religion_memory_backup_*.db | tail -n +8 | xargs rm -f
EOF

chmod +x backup.sh

# Add to crontab for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/ai-religion-architects/backup.sh") | crontab -
```

### 5.3 Log Rotation

```bash
# Configure logrotate
sudo cat > /etc/logrotate.d/ai-religion-architects << 'EOF'
/opt/ai-religion-architects/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
```

## Step 6: Continuous Deployment

The system is configured for automatic deployment:

1. **Push to main branch** → GitHub Actions builds Docker image
2. **Image pushed to registry** → VPS pulls and restarts containers
3. **Frontend changes** → Vercel automatically deploys

### Manual deployment commands:

```bash
# On VPS - manual update
cd /opt/ai-religion-architects
git pull origin main
docker-compose pull
docker-compose up -d --force-recreate
```

## Troubleshooting

### Common Issues

1. **WebSocket connection fails**
   ```bash
   # Check if port 8000 is accessible
   curl -f http://your-domain.com:8000/
   
   # Check nginx logs
   docker-compose logs nginx
   ```

2. **Database corruption**
   ```bash
   # Restore from backup
   cp data/religion_memory_backup_YYYYMMDD_HHMMSS.db data/religion_memory.db
   docker-compose restart ai-religion-architects
   ```

3. **High CPU usage**
   ```bash
   # Reduce cycle frequency
   # Edit docker-compose.yml and set CYCLE_DELAY=10 (or higher)
   docker-compose up -d
   ```

4. **Frontend not updating**
   - Check Vercel deployment logs
   - Verify WebSocket URL in configuration
   - Clear browser cache

### Monitoring

```bash
# System resources
htop
df -h

# Docker stats
docker stats

# Application logs
tail -f logs/debate_session_*.log
```

## Production Considerations

1. **Resource Limits**: Set appropriate memory/CPU limits in docker-compose.yml
2. **Rate Limiting**: Consider adding rate limiting to API endpoints
3. **Security**: Use HTTPS, secure SSH, firewall rules
4. **Monitoring**: Set up uptime monitoring (UptimeRobot, etc.)
5. **Alerts**: Configure alerts for container failures
6. **Scaling**: For high traffic, consider load balancing multiple instances

## Support

For deployment issues:
1. Check GitHub Actions logs
2. Review VPS system logs: `journalctl -u docker`
3. Monitor application logs: `docker-compose logs -f`
4. Verify network connectivity and DNS settings