# ⚡ Aura — Enterprise-Grade Spaza Platform

> A hardened, community-centric service and delivery platform connecting South Africans to trusted local Spaza shops.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![Security](https://img.shields.io/badge/ModSecurity-WAF-red?logo=target)](https://owasp.org/www-project-modsecurity-core-rule-set/)

---

## 🛡️ Security Architecture

- **WAF Protection**: Nginx with **OWASP ModSecurity Core Rule Set** — blocks XSS, SQLi, and common exploits.
- **Identity Control**: Mandatory **TOTP Multi-Factor Authentication (MFA)** for all admin accounts.
- **Data Integrity**: Full **SQLAlchemy ORM** with atomic transactions for orders and account management.
- **Network Hardening**: Reverse proxy with automatic HTTPS redirection and strict TLSv1.2+ protocols.
- **Container Isolation**: Multi-stage builds running as a **non-root user** (`aurauser`) to minimize attack surface.

---

## 🚀 Installation & Setup

### Prerequisites
- [Docker Engine](https://docs.docker.com/get-docker/) (v20.10+) & Docker Compose V2
- `git` installed

### 1. Clone the Repository
```bash
git clone git@github.com:thulanesigasa/Aura.git
cd Aura
```

### 2. Configure Environment Variables
Create a `.env` file in the project root:
```bash
SECRET_KEY="your-super-secret-key-here"
DATABASE_URL="postgresql://aura_user:aura_pass@db:5432/aura_db"
POSTGRES_USER="aura_user"
POSTGRES_PASSWORD="aura_pass"
POSTGRES_DB="aura_db"
```

### 3. Build & Launch
```bash
docker compose up -d --build
```

This starts three containers:

| Container | Image | Role |
|-----------|-------|------|
| `aura-db` | `postgres:16-alpine` | PostgreSQL database |
| `aura-web` | `aura-web` | Flask/Gunicorn app server |
| `aura-proxy` | `aura-nginx` | Nginx reverse proxy with WAF |

### 4. Verify Everything Is Running
```bash
docker compose ps
```
All three containers should show a **healthy** status. Example output:
```
NAME         IMAGE                STATUS                  PORTS
aura-db      postgres:16-alpine   Up (healthy)            5432/tcp
aura-proxy   aura-nginx           Up (healthy)            0.0.0.0:80->8080/tcp, 0.0.0.0:443->8443/tcp
aura-web     aura-web             Up (healthy)            8000/tcp
```

### 5. Open in Your Browser

| URL | Description |
|-----|-------------|
| [http://localhost](http://localhost) | Redirects to HTTPS automatically |
| [https://localhost](https://localhost) | Main application (accept the self-signed cert warning) |

> **Note:** Since the app uses a self-signed SSL certificate, your browser will show a security warning. Click **Advanced** → **Proceed to localhost** to continue.

---

## 🛠️ Management & Operations

### Access Points
| Service | URL | Protected By |
|---------|-----|--------------|
| **Public Portal** | [https://localhost](https://localhost) | Nginx WAF |
| **Admin Login** | [https://localhost/admin/login](https://localhost/admin/login) | MFA + Rate Limit |
| **Sitemap** | [https://localhost/sitemap.xml](https://localhost/sitemap.xml) | Public |

### Common Commands
```bash
# View logs
docker compose logs web --tail 50
docker compose logs nginx --tail 50

# Restart services
docker compose restart

# Stop all containers
docker compose down

# Rebuild after code changes
docker compose up -d --build
```

### Automation Scripts
Located in the `scripts/` directory:
- `./scripts/backup.sh` — Atomic PostgreSQL backup (stored in `backups/`).
- `./scripts/security_audit.sh` — Run `pip-audit` to find vulnerable dependencies.

---

## 🌍 Deployment (Huawei Cloud)

1. **SWR Registry**: Push images to Huawei Cloud Software Repository for Container.
2. **CCE Engine**: Deploy using Cloud Container Engine for high availability.
3. **WAF Service**: Use Huawei Cloud WAF alongside the local ModSecurity WAF for global DDoS protection.
4. **RDS**: Replace the local `db` container with a managed **RDS PostgreSQL** instance.

---

## 🔍 SEO & Visibility
- **Dynamic Sitemap**: Auto-updates as new shops register.
- **JSON-LD Schema**: Implements `LocalBusiness` and `Organization` types for rich search snippets.
- **Semantic HTML**: Optimized for accessibility and indexing.

---

## 📄 License
MIT © 2026 [thulanesigasa](https://github.com/thulanesigasa)
