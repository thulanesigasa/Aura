# ⚡ Aura — Enterprise-Grade Spaza Platform

> A hardened, community-centric service and delivery platform connecting South Africans to trusted local Spaza shops.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![Security](https://img.shields.io/badge/ModSecurity-WAF-red?logo=target)](https://owasp.org/www-project-modsecurity-core-rule-set/)

---

## 🛡️ Security Architecture

Aura has been overhauled with enterprise-grade security measures:
- **WAF Protection**: Integrated **Nginx with ModSecurity** (OWASP Core Rule Set) to block XSS, SQLi, and common exploits.
- **Identity Control**: Mandatory **TOTP Multi-Factor Authentication (MFA)** for all administrative accounts.
- **Data Integrity**: Full **SQLAlchemy ORM** implementation with atomic transactions for orders and account management.
- **Network Hardening**: Secure reverse proxy with automated HTTPS redirection and strict TLSv1.2+ protocols.
- **Container Isolation**: Multi-stage builds running as a **non-root user** (`aurauser`) to minimize attack surface.

---

## 🚀 Installation & Setup

### Prerequisites
- [Docker Engine](https://docs.docker.com/get-docker/) & Docker Compose V2
- A terminal with `git` and `bash` support

### 1. Clone & Configure
```bash
git clone git@github.com:thulanesigasa/Aura.git
cd Aura
cp .env.example .env  # If provided, or create one
```

### 2. Environment Variables
Create a `.env` file in the root directory:
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

---

## 🛠️ Management & Operations

### Access Points
| Service | Local URL | Protected By |
|---------|-----------|--------------|
| **Public Portal** | [https://localhost](https://localhost) | Nginx WAF |
| **Admin Login** | [https://localhost/admin/login](https://localhost/admin/login) | MFA + Rate Limit |
| **Sitemap** | [https://localhost/sitemap.xml](https://localhost/sitemap.xml) | Public |

### Automation Scripts
Located in the `scripts/` directory:
- `./scripts/backup.sh`: Perform an atomic PostgreSQL backup (stored in `backups/`).
- `./scripts/security_audit.sh`: Run `pip-audit` against the current environment to find vulnerable dependencies.

---

## 🌍 Deployment (Huawei Cloud)

1. **SWR Registry**: Push images to Huawei Cloud Software Repository for Container.
2. **CCE Engine**: Deploy using Cloud Container Engine for high availability.
3. **WAF Service**: While we include a local ModSecurity WAF, it is recommended to also use Huawei Cloud WAF for global DDOS protection.
4. **RDS**: Replace the local `db` container with a managed **Relational Database Service (PostgreSQL)** instance.

---

## 🔍 SEO & Visibility
- **Dynamic Sitemap**: Auto-updates as new shops register.
- **JSON-LD Schema**: Implements `LocalBusiness` and `Organization` types for rich search snippets.
- **Semantic HTML**: Fully optimized for accessibility and indexing.

---

## 📄 License
MIT © 2026 [thulanesigasa](https://github.com/thulanesigasa)
