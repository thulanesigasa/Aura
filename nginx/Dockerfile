FROM owasp/modsecurity-crs:nginx-alpine

# Copy custom ModSecurity config
COPY modsec/main.conf /etc/nginx/modsec/main.conf

# Copy SSL certificates to where the OWASP image expects them
# and ensure readable by the unprivileged nginx user
COPY ssl/aura.crt /etc/nginx/conf/server.crt
COPY ssl/aura.key /etc/nginx/conf/server.key

USER root
RUN chmod 644 /etc/nginx/conf/server.crt /etc/nginx/conf/server.key
USER nginx

EXPOSE 8080 8443
