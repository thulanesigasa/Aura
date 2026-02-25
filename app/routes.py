"""Flask routes for the Aura platform."""

import json
from flask import Blueprint, render_template, Response, abort
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

@bp.route("/admin/<shop_name>")
def admin_dashboard(shop_name):
    """Hidden admin dashboard for shop owners."""
    shop = _fetch_shop_by_slug(shop_name)
    if not shop:
        abort(404)
    products = _fetch_products_for_shop(shop["id"])
    return render_template("admin.html", shop=shop, products=products)


@bp.route("/admin/api/product/<int:product_id>/toggle", methods=["POST"])
def toggle_product_stock(product_id):
    """Toggle the in_stock boolean for a given product."""
    try:
        db = get_db()
        cur = db.cursor()
        
        # Get current status
        cur.execute("SELECT in_stock FROM products WHERE id = %s;", (product_id,))
        row = cur.fetchone()
        if not row:
            return Response(json.dumps({"error": "Product not found"}), status=404, mimetype="application/json")
            
        new_status = not row[0]
        
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
