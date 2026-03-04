# ⚡ Aura — Enterprise-Grade Spaza Platform

**Live Deployment URL:** [https://122.8.134.223](https://122.8.134.223)
> **⚠️ Judge's Note:** The platform is securely deployed on a Huawei Cloud ECS using a custom Nginx reverse proxy. It currently uses a self-signed SSL certificate. When accessing the URL, your browser will show a security warning. Please click **"Advanced"** → **"Proceed to 122.8.134.223 (unsafe)"** to view the live platform.

### Competition Details
* **Team Name:** DevPips
* **Team Members:** thulane_sigasa, hid_nd1jz6yr2_ihupa
* **Track:** Theme 1: Community-Based Service & Delivery Platform

---

## 📖 Executive Summary
Aura is a hardened, community-centric service and delivery platform designed to connect South African citizens with their trusted local Spaza shops. It bridges the digital divide for small business owners in Standerton by providing an accessible, zero-commission digital storefront, real-time order tracking, and a built-in delivery team management system.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![Security](https://img.shields.io/badge/ModSecurity-WAF-red?logo=target)](https://owasp.org/www-project-modsecurity-core-rule-set/)

---

## 🔗 Application Portals

The following portals are fully functional on the live server:

| Portal | Live URL | Who uses it |
|--------|-----|-------------|
| 🛍️ **Customer Directory** | [`https://122.8.134.223`](https://122.8.134.223) | Customers browsing shops & placing orders |
| 📦 **Track an Order** | [`https://122.8.134.223/track`](https://122.8.134.223/track) | Clients tracking by order ID or phone number |
| 🔐 **Admin Login** | [`https://122.8.134.223/admin/login`](https://122.8.134.223/admin/login) | Shop owners — manage products, orders & delivery team |
| 🚲 **Delivery Portal** | [`https://122.8.134.223/driver/login`](https://122.8.134.223/driver/login) | Delivery people — view assigned orders, update status, share live GPS |

---

## 🛡️ Huawei Cloud Architecture & Security
The platform is fully containerized and deployed on a Huawei Cloud Elastic Cloud Server (ECS) running Ubuntu 22.04 LTS (2 vCPUs, 2GiB Memory) in the AF-Johannesburg region.

Security was treated as a first-class citizen:
- **WAF Protection**: Nginx with **OWASP ModSecurity Core Rule Set** blocks XSS, SQLi, and common exploits.
- **Identity Control**: Mandatory **TOTP Multi-Factor Authentication (MFA)** for all shop admin accounts.
- **Network Hardening**: Reverse proxy with automatic HTTPS redirection.
- **Container Isolation**: Multi-stage Docker builds running as a **non-root user** (`aurauser`) to minimize the attack surface.

---

## 🚲 Custom Delivery System (No Paid APIs)
Aura features a custom-built, Uber-style live tracking system that uses **zero paid APIs**, keeping costs nonexistent for Spaza owners:
- **GPS**: Native browser `navigator.geolocation` allows delivery staff to broadcast locations from any standard smartphone browser without installing an app.
- **Maps**: Open-source Leaflet.js with free CartoDB dark tiles.
- **Real-time**: Simple 5-second asynchronous polling.

---

## 🚀 Local Evaluation Setup (Optional)
The project is already live on Huawei Cloud, but if judges wish to evaluate the code locally:

### Prerequisites
* Docker Engine (v20.10+) & Docker Compose V2

### Build & Start
```bash
# 1. Clone or extract the repository
cd Aura

# 2. Build and start the containers
docker-compose up -d --build
