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


# ── SEO endpoints ────────────────────────────────────────────────────────────

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
