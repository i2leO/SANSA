# SANSA Deployment Guide

This guide covers deploying the SANSA system to production environments.

## 📋 Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Production Configuration](#production-configuration)
- [Deployment Options](#deployment-options)
- [Security Hardening](#security-hardening)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)

## Pre-Deployment Checklist

### Backend

- [ ] All tests passing
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] JWT secret key is strong (32+ chars)
- [ ] CORS origins set correctly
- [ ] File upload limits configured
- [ ] Logging configured
- [ ] Error handling reviewed
- [ ] Rate limiting implemented (if needed)
- [ ] API documentation accessible

### Frontend

- [ ] Production build successful
- [ ] Environment variables set
- [ ] API URL points to production
- [ ] No console errors
- [ ] All routes tested
- [ ] Forms validated
- [ ] Error boundaries in place
- [ ] Accessibility tested

### Database

- [ ] Backup strategy in place
- [ ] Migrations tested on copy
- [ ] Indexes optimized
- [ ] Connection pooling configured
- [ ] SSL/TLS enabled
- [ ] User permissions restricted

### Infrastructure

- [ ] SSL certificates obtained
- [ ] Domain configured
- [ ] Firewall rules set
- [ ] Server capacity adequate
- [ ] Monitoring tools ready
- [ ] Backup storage available

## Production Configuration

### Backend Configuration

**Environment Variables (.env):**

```env
# Application
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=mysql+pymysql://user:pass@prod-db-server:3306/sansa_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Security
JWT_SECRET_KEY=<STRONG-RANDOM-KEY-MIN-32-CHARS>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
FRONTEND_URL=https://yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# File Uploads
UPLOAD_DIR=/var/www/sansa/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes

# Email (if implemented)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=<smtp-password>

# Monitoring
SENTRY_DSN=<sentry-dsn>  # Optional
```

### Frontend Configuration

**Environment Variables (.env.production):**

```env
VITE_API_URL=https://api.yourdomain.com
VITE_APP_VERSION=1.0.0
VITE_ENABLE_ANALYTICS=true
```

### Database Configuration

**MySQL Production Settings:**

```sql
-- Create production database
CREATE DATABASE sansa_prod
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Create dedicated user
CREATE USER 'sansa_user'@'%' IDENTIFIED BY '<strong-password>';
GRANT SELECT, INSERT, UPDATE, DELETE ON sansa_prod.* TO 'sansa_user'@'%';
FLUSH PRIVILEGES;
```

**my.cnf optimizations:**

```ini
[mysqld]
# Performance
innodb_buffer_pool_size = 2G
innodb_log_file_size = 256M
max_connections = 200
query_cache_size = 0
query_cache_type = 0

# Security
ssl-ca=/path/to/ca.pem
ssl-cert=/path/to/server-cert.pem
ssl-key=/path/to/server-key.pem
require_secure_transport=ON

# Logging
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
```

## Deployment Options

### Option 1: Traditional VPS (Ubuntu 22.04)

**1. Prepare Server:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip
sudo apt install -y nginx mysql-server
sudo apt install -y git curl

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install certbot for SSL
sudo apt install -y certbot python3-certbot-nginx
```

**2. Deploy Backend:**

```bash
# Create app user
sudo useradd -m -s /bin/bash sansa
sudo su - sansa

# Clone repository
git clone <repository-url> ~/sansa
cd ~/sansa/backend

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with production values

# Run migrations
alembic upgrade head

# Seed database
python scripts/seed.py

# Exit back to root
exit
```

**3. Setup Systemd Service:**

```bash
sudo nano /etc/systemd/system/sansa-api.service
```

```ini
[Unit]
Description=SANSA FastAPI Application
After=network.target mysql.service

[Service]
Type=notify
User=sansa
Group=sansa
WorkingDirectory=/home/sansa/sansa/backend
Environment="PATH=/home/sansa/sansa/backend/venv/bin"
ExecStart=/home/sansa/sansa/backend/venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-config logging.conf
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable sansa-api
sudo systemctl start sansa-api
sudo systemctl status sansa-api
```

**4. Deploy Frontend:**

```bash
# Build frontend
cd ~/sansa/frontend
npm install
npm run build

# Move to web directory
sudo mkdir -p /var/www/sansa
sudo cp -r dist/* /var/www/sansa/
sudo chown -R www-data:www-data /var/www/sansa
```

**5. Configure Nginx:**

```bash
sudo nano /etc/nginx/sites-available/sansa
```

```nginx
# API Server
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # File uploads
    client_max_body_size 10M;
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /var/www/sansa;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/sansa /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**6. Setup SSL:**

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
sudo certbot --nginx -d api.yourdomain.com
```

### Option 2: Docker Deployment

**Backend Dockerfile:**

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations on startup
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend Dockerfile:**

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Docker Compose:**

```yaml
# docker-compose.yml
version: "3.8"

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: sansa_prod
      MYSQL_USER: sansa_user
      MYSQL_PASSWORD: ${DB_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    restart: always

  backend:
    build: ./backend
    environment:
      DATABASE_URL: mysql+pymysql://sansa_user:${DB_PASSWORD}@db:3306/sansa_prod
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      FRONTEND_URL: https://yourdomain.com
    volumes:
      - uploads:/app/uploads
    ports:
      - "8000:8000"
    depends_on:
      - db
    restart: always

  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: always

volumes:
  mysql_data:
  uploads:
```

**Deploy with Docker:**

```bash
# Create .env file with secrets
cat > .env << EOF
DB_PASSWORD=<strong-password>
DB_ROOT_PASSWORD=<strong-root-password>
JWT_SECRET_KEY=<strong-jwt-secret>
EOF

# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed database
docker-compose exec backend python scripts/seed.py
```

### Option 3: Cloud Platforms

**AWS Elastic Beanstalk:**

1. Install AWS CLI and EB CLI
2. Initialize: `eb init`
3. Create environment: `eb create production`
4. Configure RDS for database
5. Deploy: `eb deploy`

**Google Cloud Run:**

1. Build containers: `gcloud builds submit`
2. Deploy: `gcloud run deploy`
3. Connect to Cloud SQL
4. Configure environment variables

**Azure App Service:**

1. Create App Service plan
2. Deploy backend: `az webapp up`
3. Deploy frontend to Static Web Apps
4. Configure Azure Database for MySQL

## Security Hardening

### Backend Security

**1. Update requirements.txt:**

```bash
pip install safety
safety check
pip-audit
```

**2. Add security headers:**

```python
# app/main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
app.add_middleware(HTTPSRedirectMiddleware)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

**3. Rate limiting:**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...
```

### Database Security

```sql
-- Restrict permissions
REVOKE ALL PRIVILEGES ON sansa_prod.* FROM 'sansa_user'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON sansa_prod.* TO 'sansa_user'@'%';

-- Enable audit logging
SET GLOBAL general_log = 'ON';

-- Regular password rotation
ALTER USER 'sansa_user'@'%' IDENTIFIED BY '<new-password>';
```

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

## Monitoring and Maintenance

### Application Monitoring

**1. Setup Logging:**

```python
# backend/logging.conf
[loggers]
keys=root,uvicorn

[handlers]
keys=console,file

[formatters]
keys=default

[logger_root]
level=INFO
handlers=console,file

[handler_file]
class=logging.handlers.RotatingFileHandler
formatter=default
args=('/var/log/sansa/app.log', 'a', 10485760, 5)
```

**2. Health Check Endpoint:**

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

**3. Setup Monitoring Service:**

```bash
# Prometheus + Grafana (example)
docker run -d -p 9090:9090 prom/prometheus
docker run -d -p 3000:3000 grafana/grafana
```

### Database Monitoring

```sql
-- Check slow queries
SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10;

-- Monitor connections
SHOW PROCESSLIST;

-- Check table sizes
SELECT
    table_name,
    ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = 'sansa_prod'
ORDER BY size_mb DESC;
```

### Performance Monitoring

```bash
# System resources
htop
iostat -x 1
vmstat 1

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Application logs
sudo journalctl -u sansa-api -f
```

## Backup and Recovery

### Automated Database Backup

```bash
#!/bin/bash
# /usr/local/bin/backup-sansa-db.sh

BACKUP_DIR="/var/backups/sansa"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="sansa_prod"
DB_USER="backup_user"
DB_PASS="backup_password"

mkdir -p $BACKUP_DIR

# Dump database
mysqldump -u$DB_USER -p$DB_PASS \
    --single-transaction \
    --routines \
    --triggers \
    $DB_NAME | gzip > $BACKUP_DIR/sansa_${DATE}.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "sansa_*.sql.gz" -mtime +7 -delete

# Upload to cloud storage (example)
aws s3 cp $BACKUP_DIR/sansa_${DATE}.sql.gz s3://sansa-backups/
```

**Setup cron job:**

```bash
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-sansa-db.sh
```

### File Backup

```bash
#!/bin/bash
# Backup uploaded files
rsync -avz /var/www/sansa/uploads/ backup-server:/backups/sansa-uploads/
```

### Restore Procedure

```bash
# Restore database
gunzip < backup.sql.gz | mysql -u root -p sansa_prod

# Restore files
rsync -avz backup-server:/backups/sansa-uploads/ /var/www/sansa/uploads/
```

## Troubleshooting

### Common Issues

**1. Database Connection Errors:**

```bash
# Check MySQL is running
sudo systemctl status mysql

# Test connection
mysql -u sansa_user -p sansa_prod

# Check logs
sudo tail -f /var/log/mysql/error.log
```

**2. Backend Won't Start:**

```bash
# Check service status
sudo systemctl status sansa-api

# View logs
sudo journalctl -u sansa-api -n 50

# Test manually
cd /home/sansa/sansa/backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**3. Frontend 404 Errors:**

```bash
# Check nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Check file permissions
ls -la /var/www/sansa
```

**4. SSL Certificate Issues:**

```bash
# Test certificate
sudo certbot certificates

# Renew manually
sudo certbot renew --dry-run
sudo certbot renew
```

### Performance Issues

**Slow Database Queries:**

```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

-- Check for missing indexes
EXPLAIN SELECT * FROM respondents WHERE code = 'RES12345678';

-- Add index if needed
CREATE INDEX idx_respondent_code ON respondents(code);
```

**High Memory Usage:**

```bash
# Check processes
ps aux --sort=-%mem | head

# Restart services
sudo systemctl restart sansa-api
```

## Rollback Procedure

If deployment fails:

```bash
# 1. Stop services
sudo systemctl stop sansa-api

# 2. Rollback database
cd /home/sansa/sansa/backend
source venv/bin/activate
alembic downgrade -1  # Or specific revision

# 3. Rollback code
git checkout previous-stable-tag

# 4. Restart services
sudo systemctl start sansa-api
```

## Post-Deployment Checklist

- [ ] All services running
- [ ] Health check responds correctly
- [ ] Can login as admin
- [ ] Can create respondent
- [ ] Can submit SANSA assessment
- [ ] Can export data
- [ ] SSL certificates valid
- [ ] Backups running
- [ ] Monitoring active
- [ ] Error alerts configured
- [ ] Documentation updated
- [ ] Team notified

---

**For production support:** [Add contact information]

**Last Updated:** January 2026
