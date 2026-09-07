# SSL/TLS Setup Guide

> **Purpose**: Configure HTTPS for all production services (API, Web, Mobile API)
> **Audience**: DevOps Engineer
> **Prerequisites**: Domain ownership, DNS access, Cloudflare account (recommended)

---

## Overview

EcoFinwize requires HTTPS for:
- **API**: `api.finwize.app` (backend FastAPI)
- **Web**: `app.finwize.app` (React frontend)
- **Admin**: `admin.finwize.app` (React admin panel)
- **Staging**: `staging-api.finwize.app`, `staging-app.finwize.app`

---

## Option A: Cloudflare (Recommended) 🌟

**Pros**: Free SSL, WAF, DDoS protection, CDN, edge caching, easy setup
**Cons**: Traffic passes through Cloudflare

### Setup Steps

1. **Add Domain to Cloudflare**
   ```
   1. Login to https://dash.cloudflare.com
   2. "Add a Site" → enter `finwize.app`
   3. Select "Free" plan
   4. Update nameservers at registrar (Namecheap, GoDaddy, etc.)
   ```

2. **DNS Records**
   ```
   Type    Name              Content                     Proxy
   A       @                 <SERVER_IP>                 ✅ Proxied
   A       api               <SERVER_IP>                 ✅ Proxied
   A       app               <SERVER_IP>                 ✅ Proxied
   A       admin             <SERVER_IP>                 ✅ Proxied
   A       staging-api       <STAGING_SERVER_IP>         ✅ Proxied
   A       staging-app       <STAGING_SERVER_IP>         ✅ Proxied
   CNAME   www               finwize.app                 ✅ Proxied
   ```

3. **SSL/TLS Settings**
   - SSL/TLS → Overview → **Full (Strict)**
   - SSL/TLS → Edge Certificates → **Always Use HTTPS: On**
   - SSL/TLS → Edge Certificates → **Automatic HTTPS Rewrites: On**
   - SSL/TLS → Edge Certificates → **Minimum TLS Version: 1.2**

4. **Security Headers (via Cloudflare Workers or Transform Rules)**
   ```
   # Add via Cloudflare Workers or Rules → Transform Rules → Modify Response Headers
   Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
   X-Content-Type-Options: nosniff
   X-Frame-Options: DENY
   Referrer-Policy: strict-origin-when-cross-origin
   Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.finwize.app wss://api.finwize.app; frame-ancestors 'none';
   Permissions-Policy: accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()
   ```

5. **WAF Rules**
   - Rate limit: `/api/v1/auth/*` → 10 req/min per IP
   - Block: Known bad bots, SQL injection patterns
   - Challenge: Suspicious traffic

6. **Page Rules**
   ```
   api.finwize.app/*     → Cache Level: Bypass, SSL: Full (Strict)
   app.finwize.app/*     → Cache Level: Standard, Edge Cache TTL: 1 hour
   *.finwize.app/*       → Always Use HTTPS: On
   ```

---

## Option B: Let's Encrypt + Nginx (Self-Hosted)

**Pros**: Full control, no third-party
**Cons**: Manual cert renewal, no WAF/CDN

### Prerequisites
- Ubuntu 22.04+ server
- Nginx installed
- Domain pointing to server IP
- Port 80, 443 open

### Setup Steps

1. **Install Certbot**
   ```bash
   sudo apt update && sudo apt install -y certbot python3-certbot-nginx
   ```

2. **Nginx Config** (`/etc/nginx/sites-available/finwize`)
   ```nginx
   # HTTP → HTTPS redirect
   server {
       listen 80;
       listen [::]:80;
       server_name api.finwize.app app.finwize.app admin.finwize.app;
       return 301 https://$server_name$request_uri;
   }

   # API Backend
   server {
       listen 443 ssl http2;
       listen [::]:443 ssl http2;
       server_name api.finwize.app;

       ssl_certificate /etc/letsencrypt/live/api.finwize.app/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/api.finwize.app/privkey.pem;
       include /etc/letsencrypt/options-ssl-nginx.conf;
       ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

       # Security headers
       add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
       add_header X-Content-Type-Options nosniff always;
       add_header X-Frame-Options DENY always;
       add_header Referrer-Policy strict-origin-when-cross-origin always;

       # Rate limiting
       limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
       limit_req zone=api burst=200 nodelay;

       location / {
           proxy_pass http://localhost:8100;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_cache_bypass $http_upgrade;
           proxy_read_timeout 300s;
           proxy_send_timeout 300s;
       }
   }

   # Frontend (React)
   server {
       listen 443 ssl http2;
       listen [::]:443 ssl http2;
       server_name app.finwize.app admin.finwize.app;

       ssl_certificate /etc/letsencrypt/live/app.finwize.app/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/app.finwize.app/privkey.pem;
       include /etc/letsencrypt/options-ssl-nginx.conf;
       ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

       root /var/www/finwize/frontend;
       index index.html;

       # Security headers
       add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
       add_header X-Content-Type-Options nosniff always;
       add_header X-Frame-Options DENY always;
       add_header Referrer-Policy strict-origin-when-cross-origin always;
       add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.finwize.app wss://api.finwize.app;" always;

       location / {
           try_files $uri $uri/ /index.html;
       }

       # Cache static assets
       location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
   }
   ```

3. **Obtain Certificates**
   ```bash
   # API
   sudo certbot --nginx -d api.finwize.app

   # Frontend (multiple domains)
   sudo certbot --nginx -d app.finwize.app -d admin.finwize.app

   # Staging
   sudo certbot --nginx -d staging-api.finwize.app -d staging-app.finwize.app
   ```

4. **Auto-Renewal**
   ```bash
   # Test renewal
   sudo certbot renew --dry-run

   # Systemd timer already installed by certbot package
   systemctl status certbot.timer
   ```

5. **Diffie-Hellman Parameters**
   ```bash
   sudo openssl dhparam -out /etc/letsencrypt/ssl-dhparams.pem 2048
   ```

---

## Option C: Platform-Managed (Railway/Vercel/Render)

**Pros**: Zero config, automatic HTTPS
**Cons**: Less control, vendor lock-in

### Railway
- Custom domains → Add domain → Railway provisions SSL automatically
- `railway domain add api.finwize.app`

### Vercel (Frontend)
- Project Settings → Domains → Add `app.finwize.app`
- Automatic SSL via Let's Encrypt

### Render
- Settings → Custom Domains → Add domain
- Automatic SSL

---

## Local Development HTTPS

For testing HTTPS locally with valid certificates:

### Using mkcert (Recommended)
```bash
# Install mkcert
# macOS: brew install mkcert
# Linux: sudo apt install libnss3-tools && go install filippo.io/mkcert@latest
# Windows: choco install mkcert

# Setup local CA
mkcert -install

# Generate certs for local domains
mkcert -key-file ./certs/localhost-key.pem -cert-file ./certs/localhost.pem \
  "localhost" "127.0.0.1" "::1" "*.localhost" "api.localhost" "app.localhost"

# Use in docker-compose.override.yml
# volumes:
#   - ./certs:/etc/nginx/certs:ro
```

### Update docker-compose for Local HTTPS
```yaml
# docker-compose.override.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.local.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - api
      - frontend
```

---

## Security Headers Checklist

| Header | Value | Purpose |
|--------|-------|---------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Force HTTPS |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Control referrer info |
| `Content-Security-Policy` | See configs above | Prevent XSS |
| `Permissions-Policy` | `accelerometer=(), camera=(), ...` | Restrict browser APIs |
| `Cross-Origin-Opener-Policy` | `same-origin` | Isolate browsing context |
| `Cross-Origin-Resource-Policy` | `same-origin` | Control resource loading |

---

## Testing SSL Configuration

```bash
# Test SSL grade (should be A+)
curl -I https://api.finwize.app/health

# Test with OpenSSL
openssl s_client -connect api.finwize.app:443 -servername api.finwize.app

# Test with testssl.sh
./testssl.sh api.finwize.app

# Check headers
curl -s -D - https://api.finwize.app/health -o /dev/null | grep -i "strict-transport\|x-content\|x-frame\|referrer\|content-security"

# SSL Labs test (public domains only)
https://www.ssllabs.com/ssltest/analyze.html?d=api.finwize.app
```

---

## Certificate Monitoring

- **Cloudflare**: Automatic monitoring, email alerts before expiry
- **Let's Encrypt**: Certbot timer + monitoring (cron: `0 0 * * * certbot renew --quiet`)
- **Expiry Alert**: Set calendar reminder 30 days before expiry
- **CT Logs**: Monitor Certificate Transparency logs for unauthorized certs

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ERR_CERT_COMMON_NAME_INVALID` | Cert doesn't match domain; re-issue with correct SANs |
| `ERR_SSL_VERSION_OR_CIPHER_MISMATCH` | Update TLS config, disable old protocols |
| `Mixed Content` warnings | Ensure all resources load via HTTPS |
| Certbot renewal fails | Check port 80 open, DNS correct, nginx config valid |
| Cloudflare 522/524 | Origin server down/slow; check backend health |

---

## Rollback Plan

If SSL breaks:
1. Revert DNS to non-proxied (Cloudflare) or previous nginx config
2. Use backup certs from `/etc/letsencrypt/archive/`
3. Contact CA support (Let's Encrypt: community.letsencrypt.org)