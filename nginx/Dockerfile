FROM owasp/modsecurity-crs:nginx-alpine

# Copy custom configuration
COPY default.conf /etc/nginx/conf.d/default.conf
COPY modsec/main.conf /etc/nginx/modsec/main.conf

# Copy SSL certificates
COPY ssl/aura.crt /etc/nginx/ssl/aura.crt
COPY ssl/aura.key /etc/nginx/ssl/aura.key

# Ensure proper permissions
RUN chmod 644 /etc/nginx/ssl/aura.crt /etc/nginx/ssl/aura.key

EXPOSE 80 443
