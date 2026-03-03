#!/bin/bash
# scripts/init_ssl.sh
# Automates Let's Encrypt SSL configuration for Huawei Cloud deployment

echo "🚀 Initializing Production SSL Environment for Aura..."

# Let's Encrypt SSL
echo "🔐 Setting up Let's Encrypt SSL Certificates..."
read -p "Enter your public domain name (e.g. yourdomain.com): " DOMAIN
read -p "Enter your email for SSL registration: " EMAIL

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "⚠️ Domain or Email not provided. Skipping SSL generation. (Using existing/self-signed certs)"
    exit 1
fi

echo "Checking for certbot..."
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot
fi

echo "Running Certbot in standalone mode to fetch Let's Encrypt certificates..."
# Stop proxy container temporarily if running, to free port 80
docker compose stop nginx 2>/dev/null

sudo certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos -m $EMAIL

if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "✅ Certificates obtained! Installing into nginx/ssl..."
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" nginx/ssl/aura.crt
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" nginx/ssl/aura.key
    
    # Ensure correct permissions
    sudo chown $USER:$USER nginx/ssl/aura.crt nginx/ssl/aura.key
    chmod 644 nginx/ssl/aura.crt nginx/ssl/aura.key
    
    echo "✅ SSL Certificates configured successfully."
    echo "Please run: 'docker compose up -d --build nginx' to apply the new certificates."
else
    echo "❌ Failed to obtain certificates."
    echo "Please check your domain DNS settings and ensure port 80 is accessible."
    exit 1
fi
