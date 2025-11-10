# Deployment Guide for Ethio Bingo

## Prerequisites

- VPS or cloud server (1GB+ RAM recommended)
- Domain name with SSL certificate
- Telegram Bot Token
- Docker and Docker Compose (recommended)

## Option 1: Docker Deployment (Recommended)

### 1. Prepare Server

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone and Configure

```bash
# Clone repository
git clone https://github.com/YonasGr/bingo.git
cd bingo

# Create .env file
cp .env.example .env
nano .env
```

Configure your .env:
```env
TELEGRAM_BOT_TOKEN=your_actual_bot_token
TELEGRAM_WEBHOOK_URL=https://yourdomain.com
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

### 3. Deploy

```bash
# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Initialize database
docker-compose exec app python -c "from src.core.database import init_db; init_db()"
```

### 4. Setup Nginx Reverse Proxy

```bash
sudo apt-get install nginx certbot python3-certbot-nginx

# Create nginx config
sudo nano /etc/nginx/sites-available/ethio-bingo
```

Nginx configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ethio-bingo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL
sudo certbot --nginx -d yourdomain.com
```

## Option 2: Manual Deployment

### 1. Prepare Server

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3.9 python3-pip python3-venv postgresql redis-server nginx

# Create user
sudo useradd -m -s /bin/bash bingo
sudo su - bingo
```

### 2. Setup Application

```bash
# Clone repository
git clone https://github.com/YonasGr/bingo.git
cd bingo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Database

```bash
# Create PostgreSQL user and database
sudo -u postgres psql
CREATE USER bingo_user WITH PASSWORD 'secure_password';
CREATE DATABASE ethio_bingo OWNER bingo_user;
\q

# Initialize database
python -c "from src.core.database import init_db; init_db()"
```

### 4. Setup Systemd Service

Create `/etc/systemd/system/ethio-bingo.service`:

```ini
[Unit]
Description=Ethio Bingo Telegram Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=bingo
WorkingDirectory=/home/bingo/bingo
Environment="PATH=/home/bingo/bingo/venv/bin"
EnvironmentFile=/home/bingo/bingo/.env
ExecStart=/home/bingo/bingo/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ethio-bingo
sudo systemctl start ethio-bingo
sudo systemctl status ethio-bingo
```

## Post-Deployment

### 1. Configure Telegram Webhook

```python
# Run this once to set webhook
from telegram import Bot
bot = Bot(token="YOUR_BOT_TOKEN")
bot.set_webhook(url="https://yourdomain.com/webhook")
```

### 2. Monitoring

```bash
# View logs
docker-compose logs -f app  # Docker
sudo journalctl -u ethio-bingo -f  # Systemd

# Check service status
docker-compose ps  # Docker
sudo systemctl status ethio-bingo  # Systemd
```

### 3. Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U bingo_user ethio_bingo > backup.sql

# Or manually
pg_dump -U bingo_user -h localhost ethio_bingo > backup.sql
```

### 4. Updates

```bash
# Docker
git pull
docker-compose build
docker-compose up -d

# Manual
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ethio-bingo
```

## Performance Tuning

### PostgreSQL

Edit `/etc/postgresql/*/main/postgresql.conf`:
```
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Redis

Edit `/etc/redis/redis.conf`:
```
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Application

Increase workers in production:
```env
WORKERS=4  # Number of CPU cores
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Setup firewall (ufw)
- [ ] Enable SSL/TLS
- [ ] Use strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Regular backups
- [ ] Keep system updated
- [ ] Monitor logs for suspicious activity
- [ ] Use fail2ban for brute force protection
- [ ] Restrict database access
- [ ] Use environment variables for secrets

## Troubleshooting

### Bot not responding
```bash
# Check logs
docker-compose logs app
# Verify webhook
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

### Database connection issues
```bash
# Check PostgreSQL
docker-compose exec postgres psql -U bingo_user -d ethio_bingo
# Test connection
telnet localhost 5432
```

### WebSocket connection fails
```bash
# Check nginx config
sudo nginx -t
# Verify WebSocket headers in nginx config
```

### High memory usage
```bash
# Check Redis memory
docker-compose exec redis redis-cli INFO memory
# Clear Redis cache if needed
docker-compose exec redis redis-cli FLUSHDB
```

## Scaling

### Horizontal Scaling

1. Use a load balancer (nginx, HAProxy)
2. Deploy multiple app instances
3. Use Redis for shared state
4. Implement sticky sessions for WebSocket

### Vertical Scaling

1. Increase server resources (CPU, RAM)
2. Optimize database queries
3. Add database indexes
4. Use Redis caching extensively

## Support

For deployment issues:
- Check logs first
- Review documentation
- Open GitHub issue
- Contact support

---

**Security Note**: Never commit .env files or secrets to version control!
