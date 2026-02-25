# ⚡ Aura — Community Spaza Shop Platform

> A community-based service and delivery platform connecting South Africans to trusted local Spaza shops.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)

---

## 🌍 Overview

**Aura** lets residents discover, browse, and order from neighbourhood Spaza shops fully online. The platform is built for **Huawei Cloud deployment** with a strict **< $100/month** budget, and is engineered for maximum **local SEO** visibility.

---

## 🗂 Project Structure

```
Aura/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── db.py                # DB helpers, schema & demo seed data
│   ├── routes.py            # URL routes (/, /shop/<slug>, /sitemap.xml)
│   ├── seo_utils.py         # Sitemap generator & JSON-LD builder
│   ├── static/
│   │   └── robots.txt       # Search engine directives
│   └── templates/
│       ├── index.html       # Homepage – shop grid
│       ├── shop.html        # Shop detail + LocalBusiness schema
│       ├── admin.html       # Hidden store owner dashboard
│       ├── about.html       # Static pages (About, Contact, Join)
│       └── 404.html         # Custom error page
├── Dockerfile               # python:3.11-slim + Gunicorn
├── docker-compose.yml       # Web + PostgreSQL services
├── requirements.txt
└── run.py                   # Entry point
```

---

## 🚀 Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose V2

### Run locally

```bash
git clone git@github.com:thulanesigasa/Aura.git
cd Aura
docker compose up -d --build
```

The app will be available at **[http://localhost:8000](http://localhost:8000)**.

| Service | URL |
|---------|-----|
| Homepage | http://localhost:8000/ |
| Shop detail | http://localhost:8000/shop/mama-zinzis-spaza |
| Admin Dashboard | http://localhost:8000/admin/mama-zinzis-spaza |
| Sitemap | http://localhost:8000/sitemap.xml |
| Robots | http://localhost:8000/robots.txt |

Stop the stack:
```bash
docker compose down
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, Tailwind CSS (CDN), Vanilla JS |
| Backend | Python 3.11, Flask 3.1, Gunicorn |
| Database | PostgreSQL 16 (Alpine) |
| Container | Docker, Docker Compose V2 |
| Target Cloud | Huawei Cloud (< $100/month) |

---

## 🔍 SEO Features

- `<link rel="canonical">` tags on every page
- **JSON-LD `LocalBusiness` schema** on all shop pages
- **JSON-LD `Organization` schema** on the homepage
- **Secure Architecture:** Hidden admin dashboards for store owners under `/admin/<slug>`
- **Responsive Navigation:** Portfolio-style retractable dropdown menu for optimal mobile UX
- Dynamic `/sitemap.xml` (auto-updates as shops are added)
- `/robots.txt` allowing full indexing with sitemap reference
- Semantic HTML5 with descriptive meta descriptions

---

## ⚙️ Environment Variables

Configure via `docker-compose.yml` or a `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `aura-production-secret-change-me` | Flask secret key |
| `DATABASE_URL` | `postgresql://aura_user:aura_pass@db:5432/aura_db` | PostgreSQL connection string |

---

## 🌐 Huawei Cloud Deployment Notes

1. Push the image to **SWR** (Software Repository for Container):
   ```bash
   docker tag aura-web swr.af-south-1.myhuaweicloud.com/<project>/aura-web:latest
   docker push swr.af-south-1.myhuaweicloud.com/<project>/aura-web:latest
   ```
2. Use **CCE** (Cloud Container Engine) or **CCI** for orchestration.
3. Use **RDS for PostgreSQL** instead of the local `db` container in production.
4. Point the `DATABASE_URL` env var to your RDS connection string.

---

## 📄 License

MIT © 2026 [thulanesigasa](https://github.com/thulanesigasa)
