"""Flask routes for the Aura platform."""

import json
from flask import Blueprint, render_template, Response, abort, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_db
from .seo_utils import generate_sitemap_xml, build_local_business_jsonld

bp = Blueprint("main", __name__)

BASE_URL = "https://aura.co.za"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _fetch_all_shops():
    """Return all shops as a list of dicts."""
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT id, name, slug, description, address, city, province, "
            "postal_code, phone, latitude, longitude, opening_hours, "
            "image_url, is_delivery FROM shops ORDER BY name;"
        )
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        cur.close()
        return [dict(zip(cols, row)) for row in rows]
    except Exception:
        return []


def _fetch_shop_by_slug(slug):
    """Return a single shop dict or None."""
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT id, name, slug, description, address, city, province, "
            "postal_code, phone, latitude, longitude, opening_hours, "
            "image_url, is_delivery FROM shops WHERE slug = %s;",
            (slug,),
        )
        cols = [d[0] for d in cur.description]
        row = cur.fetchone()
        cur.close()
        return dict(zip(cols, row)) if row else None
    except Exception:
        return None


def _fetch_shop_by_id(shop_id):
    """Return a single shop dict or None by ID."""
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT id, name, slug, description, address, city, province, "
            "postal_code, phone, latitude, longitude, opening_hours, "
            "image_url, is_delivery FROM shops WHERE id = %s;",
            (shop_id,),
        )
        cols = [d[0] for d in cur.description]
        row = cur.fetchone()
        cur.close()
        return dict(zip(cols, row)) if row else None
    except Exception:
        return None


def _fetch_products_for_shop(shop_id):
    """Return products for a given shop id."""
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT id, name, price, category, in_stock "
            "FROM products WHERE shop_id = %s ORDER BY category, name;",
            (shop_id,),
        )
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        cur.close()
        return [dict(zip(cols, row)) for row in rows]
    except Exception:
        return []


# ── Pages ────────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    """Homepage – list all nearby Spaza shops."""
    shops = _fetch_all_shops()
    return render_template("index.html", shops=shops, base_url=BASE_URL)


@bp.route("/shop/<shop_name>")
def shop_detail(shop_name):
    """Individual shop page with JSON-LD schema."""
    shop = _fetch_shop_by_slug(shop_name)
    if not shop:
        abort(404)
    products = _fetch_products_for_shop(shop["id"])
    jsonld = build_local_business_jsonld(shop, base_url=BASE_URL)
    return render_template(
        "shop.html",
        shop=shop,
        products=products,
        jsonld=json.dumps(jsonld),
        base_url=BASE_URL,
    )


@bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@bp.route("/terms")
def terms():
    return render_template("terms.html")


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/contact")
def contact():
    return render_template("contact.html")


@bp.route("/join")
def join():
    return render_template("join.html")


# ── Admin endpoints ──────────────────────────────────────────────────────────

@bp.route("/admin/")
def admin_root():
    """Redirect /admin/ to dashboard or login."""
    if "user_id" not in session:
        return redirect(url_for("main.admin_login"))
    
    shop = _fetch_shop_by_id(session.get("shop_id"))
    if not shop:
        # Should not happen if data is consistent, but handle it
        session.clear()
        return redirect(url_for("main.admin_login"))
        
    return redirect(url_for("main.admin_dashboard", shop_name=shop["slug"]))


@bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Login for shop owners."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, shop_id, password_hash FROM users WHERE email = %s;", (email,))
        user = cur.fetchone()
        cur.close()
        
        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["shop_id"] = user[1]
            shop = _fetch_shop_by_id(user[1])
            return redirect(url_for("main.admin_dashboard", shop_name=shop["slug"]))
        else:
            return render_template("login.html", error="Invalid email or password")
            
    return render_template("login.html")


@bp.route("/admin/signup", methods=["GET", "POST"])
def admin_signup():
    """Signup for new shop owners – creating a new shop automatically with full details."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        shop_name = request.form.get("shop_name")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone = request.form.get("phone")
        address = request.form.get("address")
        city = request.form.get("city", "Standerton")
        province = request.form.get("province", "Mpumalanga")
        
        if not email or not password or not shop_name or not first_name or not last_name or not phone:
            return render_template("signup.html", error="Basic info and Shop Name are required")
            
        db = get_db()
        cur = db.cursor()
        
        # Check if email exists
        cur.execute("SELECT id FROM users WHERE email = %s;", (email,))
        if cur.fetchone():
            cur.close()
            return render_template("signup.html", error="Email already registered")
            
        # Generate slug from shop name
        import re
        slug = re.sub(r'[^a-zA-Z0-9]', '-', shop_name.lower()).strip('-')
        # Ensure slug unique
        cur.execute("SELECT id FROM shops WHERE slug = %s;", (slug,))
        if cur.fetchone():
            import time
            slug = f"{slug}-{int(time.time() % 1000)}"

        try:
            # 1. Create the Shop with full address/city/province
            cur.execute(
                "INSERT INTO shops (name, slug, address, city, province, phone) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                (shop_name, slug, address, city, province, phone)
            )
            shop_id = cur.fetchone()[0]
            
            # 2. Create the User with owner details
            password_hash = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (shop_id, first_name, last_name, phone, email, password_hash) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                (shop_id, first_name, last_name, phone, email, password_hash)
            )
            user_id = cur.fetchone()[0]
            cur.close()
            
            session["user_id"] = user_id
            session["shop_id"] = shop_id
            return redirect(url_for("main.admin_dashboard", shop_name=slug))
        except Exception as e:
            return render_template("signup.html", error=f"Registration failed: {e}")
            
    return render_template("signup.html")


@bp.route("/admin/logout")
def admin_logout():
    """Logout shop owner."""
    session.clear()
    return redirect(url_for("main.index"))


@bp.route("/admin/<shop_name>")
def admin_dashboard(shop_name):
    """Hidden admin dashboard for shop owners."""
    if "user_id" not in session:
        return redirect(url_for("main.admin_login"))
        
    shop = _fetch_shop_by_slug(shop_name)
    if not shop or shop["id"] != session.get("shop_id"):
        abort(403) # Forbidden if trying to access other shop's admin
        
    products = _fetch_products_for_shop(shop["id"])
    return render_template("admin.html", shop=shop, products=products)


@bp.route("/admin/api/product/<int:product_id>/toggle", methods=["POST"])
def toggle_product_stock(product_id):
    """Toggle the in_stock boolean for a given product."""
    if "user_id" not in session:
        return Response(json.dumps({"error": "Unauthorized"}), status=401, mimetype="application/json")
        
    try:
        db = get_db()
        cur = db.cursor()
        
        # Verify ownership
        cur.execute("SELECT shop_id, in_stock FROM products WHERE id = %s;", (product_id,))
        row = cur.fetchone()
        if not row:
            return Response(json.dumps({"error": "Product not found"}), status=404, mimetype="application/json")
            
        if row[0] != session.get("shop_id"):
            return Response(json.dumps({"error": "Forbidden"}), status=403, mimetype="application/json")
            
        new_status = not row[1]
        
        # Update status
        cur.execute("UPDATE products SET in_stock = %s WHERE id = %s;", (new_status, product_id))
        cur.close()
        
        return Response(json.dumps({"success": True, "in_stock": new_status}), status=200, mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype="application/json")


# ── SEO endpoints ───────────────────────────────────────────────────────────

@bp.route("/sitemap.xml")
def sitemap():
    """Dynamically generated sitemap."""
    shops = _fetch_all_shops()
    xml = generate_sitemap_xml(shops, base_url=BASE_URL)
    return Response(xml, mimetype="application/xml")


@bp.route("/robots.txt")
def robots():
    """Serve robots.txt from static folder."""
    return bp.send_static_file("robots.txt")


# ── Error handlers ───────────────────────────────────────────────────────────

@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@bp.app_errorhandler(403)
def forbidden(e):
    return render_template("404.html"), 403 # Reuse 404 or create a 403 if needed
