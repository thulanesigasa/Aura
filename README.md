# ⚡ Aura — Enterprise-Grade Spaza Platform

> A hardened, community-centric service and delivery platform connecting South Africans to trusted local Spaza shops — with real-time order tracking, Uber-style live delivery maps, and a built-in delivery team management system.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![Security](https://img.shields.io/badge/ModSecurity-WAF-red?logo=target)](https://owasp.org/www-project-modsecurity-core-rule-set/)

---

## 🔗 Application Portals

Once the app is running, the following pages are available at `https://localhost`:

| Portal | URL | Who uses it |
|--------|-----|-------------|
| 🛍️ **Client / Public** | [`https://localhost`](https://localhost) | Customers browsing shops & placing orders |
| 📦 **Track an Order** | [`https://localhost/track`](https://localhost/track) | Clients tracking by order ID or phone number |
| 🔐 **Admin Login** | [`https://localhost/admin/login`](https://localhost/admin/login) | Shop owners — manage products, orders & delivery team |
| 🚲 **Delivery Portal** | [`https://localhost/driver/login`](https://localhost/driver/login) | Delivery people — view assigned orders, update status, share live GPS |

> **Note:** The app uses a self-signed SSL certificate so your browser will show a security warning. Click **Advanced → Proceed to localhost** to continue.

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

| Tool | Version | Install Guide |
|------|---------|---------------|
| **Docker Engine** | v20.10+ | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| **Docker Compose V2** | v2.0+ | Included with Docker Desktop / `apt install docker-compose-plugin` |
| **Git** | any | [git-scm.com](https://git-scm.com/) |

> **No Python or pip install needed** — everything runs inside Docker containers.

---

### Step 1 — Clone the Repository

```bash
git clone git@github.com:thulanesigasa/Aura.git
cd Aura
```

---

### Step 2 — Environment Configuration

For development, you can use basic credentials. **For Production on Huawei Cloud**, ensure you use cryptographically secure values.
We have pre-configured a secure `.env` file in this repository.

> Generate a new secure `SECRET_KEY` anytime with: `python3 -c "import secrets; print(secrets.token_hex(32))"`

---

### Step 3 — Build & Start

```bash
docker compose up -d --build
```

This builds and starts three containers:

| Container | Image | Role |
|-----------|-------|------|
| `aura-db` | `postgres:16-alpine` | PostgreSQL 16 database |
| `aura-web` | `aura-web` (custom) | Flask app served by Gunicorn |
| `aura-proxy` | `aura-nginx` (custom) | Nginx reverse proxy + ModSecurity WAF |

The database tables are created automatically on first boot.

---

### Step 4 — Verify Health

```bash
docker compose ps
```

All three containers should show **healthy**:

```
NAME         IMAGE                STATUS           PORTS
aura-db      postgres:16-alpine   Up (healthy)     5432/tcp
aura-proxy   aura-nginx           Up (healthy)     0.0.0.0:80->8080/tcp, 0.0.0.0:443->8443/tcp
aura-web     aura-web             Up (healthy)     8000/tcp
```

---

### Step 5 — Create Your First Admin Account

```bash
docker compose exec web python3 -c "
from app import create_app
from app.models import db, User, Shop

app = create_app()
with app.app_context():
    # Create a shop first
    shop = Shop(name='My Shop', slug='my-shop')
    db.session.add(shop)
    db.session.flush()

    # Create admin user linked to shop
    u = User(email='admin@example.com', shop_id=shop.id)
    u.set_password('changeme')
    db.session.add(u)
    db.session.commit()
    print('Admin created! Go to /admin/login')
"
```

Then visit [`https://localhost/admin/login`](https://localhost/admin/login) and complete the MFA setup on first login.

---

## 🛠️ Common Commands

```bash
# View application logs
docker compose logs web --tail 50

# View Nginx / WAF logs
docker compose logs nginx --tail 50

# Restart all services (e.g. after config changes)
docker compose restart

# Stop all containers
docker compose down

# Rebuild and restart after code changes
docker compose up -d --build

# Open a Python shell inside the running container
docker compose exec web python3
```

---

## 📱 Feature Overview

### For Customers
- Browse shops by city/location
- Add items to cart and place orders
- Track order by **Order ID** or **phone number** at `/track`
- Live delivery map — see your delivery person's GPS location in real time when they're on the way

### For Admins (`/admin`)
- Manage products (add, edit, archive, stock toggle)
- View incoming orders with live status updates
- **Manage Delivery Team** — add delivery people (walkers, cyclists, drivers — any transport)
- Assign orders to delivery people from the orders sidebar

### For Delivery People (`/driver/login`)
- Log in with email & password (no app install needed — works in any mobile browser)
- See active assigned orders with delivery address and items
- Update order status: **Picked Up → On My Way → Delivered**
- When "On My Way" is tapped, GPS location is automatically shared every 5 seconds so customers can track in real time

---

## 🚲 Delivery System — No Paid Services

The live tracking system uses **zero paid APIs**:

- **GPS**: Native browser `navigator.geolocation` — works on any smartphone browser
- **Maps**: [Leaflet.js](https://leafletjs.com/) (open source) with CartoDb dark tiles (free)
- **Real-time**: Simple 5-second polling — no WebSockets needed
- **Transport**: Works for cars, motorbikes, bicycles, or walking

---

## 🌍 Deployment (Huawei Cloud)

Before driving real traffic to the site on your Huawei Elastic Cloud Server (ECS), you must prepare the environment for production:

1. **Production SSL Certificates**: 
   The default setup uses self-signed certificates. To prevent browser security warnings, run the Let's Encrypt setup script:
   ```bash
   ./scripts/init_ssl.sh
   # Follow the prompts, then rebuild the proxy:
   docker compose up -d --build nginx
   ```

2. **Production Credentials**:
   Ensure `SECRET_KEY` and your database passwords in the `.env` file are set to cryptographically secure values.

3. **SWR Registry**: Push images to Huawei Cloud Software Repository for Container.
4. **CCE Engine**: Deploy using Cloud Container Engine for high availability.
5. **WAF Service**: Use Huawei Cloud WAF alongside local ModSecurity for global DDoS protection.
6. **RDS**: Replace the local `db` container with a managed **RDS PostgreSQL** instance.

---

## 🔍 SEO & Visibility

- **Dynamic Sitemap**: Auto-updates as new shops register (`/sitemap.xml`)
- **JSON-LD Schema**: Implements `LocalBusiness` and `Organization` types for rich search snippets
- **Semantic HTML**: Optimised for accessibility and search indexing

---

## 🔧 Automation Scripts

Located in `scripts/`:

```bash
./scripts/backup.sh          # Atomic PostgreSQL backup → saved to backups/
./scripts/security_audit.sh  # Run pip-audit to scan for vulnerable dependencies
```

---

## 📄 License

MIT © 2026 [thulanesigasa](https://github.com/thulanesigasa)
