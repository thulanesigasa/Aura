"""Flask routes for the Aura platform."""

import os
import json
import pyotp
import qrcode
import io
import base64
from flask import Blueprint, render_template, Response, abort, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from .models import db, Shop, Product, User, Order, OrderItem
from .seo_utils import generate_sitemap_xml, build_local_business_jsonld
from . import limiter

bp = Blueprint("main", __name__)

BASE_URL = "https://aura.co.za"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _fetch_all_shops():
    """Return filtered shops based on count: first 3 if < 10, random 3 if >= 10. Includes manager info."""
    try:
        count = Shop.query.count()
        
        if count < 10:
            # Show first three that registered
            shops_query = Shop.query.order_by(Shop.id.asc()).limit(3).all()
        else:
            # Show 3 random shops as we scale
            shops_query = Shop.query.order_by(func.random()).limit(3).all()
            
        shops = []
        for shop in shops_query:
            # Convert to dict for template compatibility or update templates to use objects
            # For now, let's keep the dict approach to minimize template changes
            shop_dict = {
                "id": shop.id,
                "name": shop.name,
                "slug": shop.slug,
                "description": shop.description,
                "address": shop.address,
                "city": shop.city,
                "province": shop.province,
                "postal_code": shop.postal_code,
                "phone": shop.phone,
                "latitude": shop.latitude,
                "longitude": shop.longitude,
                "opening_hours": shop.opening_hours,
                "image_url": shop.image_url,
                "is_delivery": shop.is_delivery,
            }
            # Find manager (first user assigned to this shop)
            manager = User.query.filter_by(shop_id=shop.id).first()
            if manager:
                shop_dict['manager_name'] = f"{manager.first_name} {manager.last_name}".strip()
            else:
                shop_dict['manager_name'] = "General Manager"
            shops.append(shop_dict)
        return shops
    except Exception as e:
        print(f"Error fetching shops: {e}")
        return []


def _fetch_shop_by_slug(slug):
    """Return a single shop record or None."""
    return Shop.query.filter_by(slug=slug).first()


def _fetch_products_for_shop(shop_id, include_archived=False):
    """Return products for a given shop. Optionally include archived ones."""
    query = Product.query.filter_by(shop_id=shop_id)
    if not include_archived:
        query = query.filter_by(is_archived=False)
    return query.order_by(Product.category, Product.name).all()


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
    products = _fetch_products_for_shop(shop.id)
    
    # Convert shop object to dict for SEO utils (unless refactored too)
    shop_dict = {
        "id": shop.id,
        "name": shop.name,
        "slug": shop.slug,
        "description": shop.description,
        "address": shop.address,
        "city": shop.city,
        "province": shop.province,
        "postal_code": shop.postal_code,
        "phone": shop.phone,
        "latitude": shop.latitude,
        "longitude": shop.longitude,
        "opening_hours": shop.opening_hours,
        "image_url": shop.image_url,
        "is_delivery": shop.is_delivery,
    }
    
    jsonld = build_local_business_jsonld(shop_dict, base_url=BASE_URL)
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


@bp.route("/checkout")
def checkout():
    """Checkout page for reviewing cart and entering delivery info."""
    return render_template("checkout.html")


@bp.route("/api/checkout", methods=["POST"])
def api_checkout():
    """Process order submission."""
    try:
        data = request.json
        shop_id = data.get("shop_id")
        customer_name = data.get("name")
        customer_phone = data.get("phone")
        delivery_address = data.get("address")
        items = data.get("items", []) # List of {product_id, quantity, price}
        
        if not items or not shop_id or not customer_name or not customer_phone or not delivery_address:
            return Response(json.dumps({"error": "Missing required fields"}), status=400, mimetype="application/json")
            
        # 1. Create main order
        total = sum(float(item['price']) * int(item['quantity']) for item in items)
        new_order = Order(
            shop_id=shop_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            delivery_address=delivery_address,
            total=total,
            status='pending'
        )
        db.session.add(new_order)
        db.session.flush() # Get ID
        
        # 2. Create order items
        for item in items:
            new_item = OrderItem(
                order_id=new_order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(new_item)
        
        db.session.commit()
        return Response(json.dumps({"success": True, "order_id": new_order.id}), status=201, mimetype="application/json")
            
    except Exception as e:
        db.session.rollback()
        return Response(json.dumps({"error": str(e)}), status=500, mimetype="application/json")


@bp.route("/order-success/<int:order_id>")
def order_success(order_id):
    """View status of a placed order."""
    order = Order.query.get_or_404(order_id)
    return render_template("order_status.html", order=order)


# ── Admin endpoints ──────────────────────────────────────────────────────────

@bp.route("/admin/")
@login_required
def admin_root():
    """Redirect /admin/ to dashboard."""
    return redirect(url_for("main.admin_dashboard"))


@bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Secure login with MFA support."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.mfa_enabled:
                # Store user ID in session for MFA verification
                session['mfa_user_id'] = user.id
                return redirect(url_for('main.mfa_verify'))
            
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("main.admin_dashboard"))
        else:
            flash("Invalid email or password.", "danger")
            
    return render_template("login.html")


def validate_password(password):
    """Ensure password is at least 8 chars and contains a number."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    return True, ""

@bp.route("/admin/signup", methods=["GET", "POST"])
def admin_signup():
    """Register a new shop and admin account within a transaction."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        shop_name = request.form.get("shop_name", "").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "Standerton").strip()
        province = request.form.get("province", "Mpumalanga").strip()

        if not email or not password or not confirm_password or not shop_name or not first_name or not last_name or not phone:
            flash("All fields are required.", "danger")
            return redirect(url_for("main.admin_signup"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("main.admin_signup"))

        try:
            # Check if email taken
            if User.query.filter_by(email=email).first():
                flash("Email already registered.", "danger")
                return redirect(url_for("main.admin_signup"))

            # 1. Create Shop
            slug = shop_name.lower().replace(" ", "-")
            if Shop.query.filter_by(slug=slug).first():
                slug = f"{slug}-{os.urandom(2).hex()}"
            
            new_shop = Shop(
                name=shop_name, 
                slug=slug, 
                address=address, 
                city=city, 
                province=province, 
                phone=phone
            )
            db.session.add(new_shop)
            db.session.flush() # Get ID

            # 2. Create User
            new_user = User(
                shop_id=new_shop.id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            new_user.set_password(password)
            db.session.add(new_user)
            
            db.session.commit()
            
            login_user(new_user)
            flash("Account created! Set up MFA for better security.", "success")
            return redirect(url_for("main.mfa_setup"))
            
        except Exception as e:
            db.session.rollback()
            print(f"Signup error: {e}")
            flash("An error occurred during registration.", "danger")

    return render_template("signup.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("main.index"))


# ── MFA Implementation ───────────────────────────────────────────────────────

@bp.route("/mfa/setup")
@login_required
def mfa_setup():
    """Generate TOTP secret and QR code for user."""
    if current_user.mfa_enabled:
        flash("MFA is already enabled.", "info")
        return redirect(url_for('main.admin_dashboard'))
    
    # Generate secret if not exists
    if not current_user.mfa_secret:
        current_user.mfa_secret = pyotp.random_base32()
        db.session.commit()
    
    # Generate QR Code
    totp = pyotp.TOTP(current_user.mfa_secret)
    provision_url = totp.provisioning_uri(name=current_user.email, issuer_name="Aura Delivery")
    
    img = qrcode.make(provision_url)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template("mfa_setup.html", qr_code=qr_base64)


@bp.route("/mfa/verify-setup", methods=["POST"])
@login_required
def mfa_verify_setup():
    """Verify the first TOTP token to enable MFA."""
    token = request.form.get("token")
    totp = pyotp.TOTP(current_user.mfa_secret)
    
    if totp.verify(token):
        current_user.mfa_enabled = True
        db.session.commit()
        flash("MFA enabled successfully!", "success")
        return redirect(url_for('main.admin_dashboard'))
    
    flash("Invalid token. Please try again.", "danger")
    return redirect(url_for('main.mfa_setup'))


@bp.route("/mfa/verify", methods=["GET", "POST"])
def mfa_verify():
    """Verify TOTP during login."""
    user_id = session.get('mfa_user_id')
    if not user_id:
        return redirect(url_for('main.admin_login'))
    
    user = User.query.get(user_id)
    if request.method == "POST":
        token = request.form.get("token")
        totp = pyotp.TOTP(user.mfa_secret)
        
        if totp.verify(token):
            login_user(user)
            session.pop('mfa_user_id', None)
            flash("Logged in successfully!", "success")
            return redirect(url_for('main.admin_dashboard'))
        
        flash("Invalid token.", "danger")
        
    return render_template("mfa_verify.html")


# ── Admin Panel (Protected) ───────────────────────────────────────────────────

@bp.route("/admin")
@login_required
def admin_dashboard():
    """Manage shop profile/inventory."""
    shop = Shop.query.get(current_user.shop_id)
    products = _fetch_products_for_shop(shop.id, include_archived=True)
    orders = Order.query.filter_by(shop_id=shop.id).order_by(Order.created_at.desc()).all()
    return render_template("admin.html", shop=shop, products=products, orders=orders)


@bp.route("/admin/update-hours", methods=["POST"])
@login_required
def update_hours():
    """Save business hours as JSON."""
    shop = Shop.query.get(current_user.shop_id)
    hours = {
        "mon-fri": {"open": request.form.get("mon-fri-open"), "close": request.form.get("mon-fri-close")},
        "sat-sun": {"open": request.form.get("sat-sun-open"), "close": request.form.get("sat-sun-close")},
        "holidays": {"open": request.form.get("holidays-open"), "close": request.form.get("holidays-close")},
    }
    shop.opening_hours = json.dumps(hours)
    db.session.commit()
    flash("Business hours updated.")
    return redirect(url_for("main.admin_dashboard"))

@bp.route("/admin/api/order/<int:order_id>/status", methods=["POST"])
@login_required
def update_order_status(order_id):
    """Update order status (e.g. pending to completed)."""
    order = Order.query.get_or_404(order_id)
    if order.shop_id != current_user.shop_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    new_status = data.get("status") if data else request.form.get("status")
    
    if new_status in ['pending', 'completed', 'cancelled']:
        order.status = new_status
        db.session.commit()
        if request.is_json:
            return jsonify({"success": True, "status": order.status})
        flash(f"Order #{order.id} status updated to {new_status}.")
    else:
        if request.is_json:
            return jsonify({"error": "Invalid status"}), 400
        flash("Invalid status update.")
        
    return redirect(url_for("main.admin_dashboard"))


@bp.route("/admin/add-product", methods=["POST"])
@login_required
def add_product():
    """Add a new product to the shop."""
    print("DEBUG request.is_json:", request.is_json, flush=True)
    print("DEBUG request.data:", request.get_data(), flush=True)
    print("DEBUG request.content_type:", request.content_type, flush=True)
    
    if request.is_json:
        data = request.json
        name = data.get("name")
        price = data.get("price")
        category = data.get("category")
        image_url = data.get("image_url")
    else:
        name = request.form.get("name")
        price = request.form.get("price")
        category = request.form.get("category")
        image_url = request.form.get("image_url")
    
    new_product = Product(
        shop_id=current_user.shop_id,
        name=name,
        price=price,
        category=category,
        image_url=image_url
    )
    db.session.add(new_product)
    db.session.commit()
    
    if request.is_json:
        return Response(json.dumps({"success": True}), status=200, mimetype="application/json")
        
    flash(f"Product '{name}' added.")
    return redirect(url_for("main.admin_dashboard"))


# ── Product API (Protected) ───────────────────────────────────────────────────

@bp.route("/admin/api/product/<int:product_id>/update", methods=["POST"])
@login_required
def update_product_api(product_id):
    """Update product name, price, category, or image."""
    data = request.json
    product = Product.query.get_or_404(product_id)
    
    if product.shop_id != current_user.shop_id:
        abort(403)
        
    product.name = data.get("name")
    product.price = data.get("price")
    product.category = data.get("category")
    product.image_url = data.get("image_url")
    
    db.session.commit()
    return Response(json.dumps({"success": True}), status=200, mimetype="application/json")


@bp.route("/admin/api/product/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product_api(product_id):
    """Remove a product from the shop."""
    product = Product.query.get_or_404(product_id)
    
    if product.shop_id != current_user.shop_id:
        abort(403)
        
    db.session.delete(product)
    db.session.commit()
    return Response(json.dumps({"success": True}), status=200, mimetype="application/json")


@bp.route("/admin/api/product/<int:product_id>/toggle", methods=["POST"])
@login_required
def toggle_product_stock_api(product_id):
    """Toggle the in_stock boolean."""
    product = Product.query.get_or_404(product_id)
    
    if product.shop_id != current_user.shop_id:
        abort(403)
        
    product.in_stock = not product.in_stock
    db.session.commit()
    return Response(json.dumps({"success": True, "in_stock": product.in_stock}), status=200, mimetype="application/json")


@bp.route("/admin/api/product/<int:product_id>/archive", methods=["POST"])
@login_required
def archive_product_api(product_id):
    """Toggle the is_archived boolean."""
    product = Product.query.get_or_404(product_id)
    
    if product.shop_id != current_user.shop_id:
        abort(403)
        
    product.is_archived = not product.is_archived
    db.session.commit()
    return Response(json.dumps({"success": True, "is_archived": product.is_archived}), status=200, mimetype="application/json")


# ── SEO & Static ─────────────────────────────────────────────────────────────

@bp.route("/admin/api/shop/hours", methods=["POST"])
@login_required
def update_shop_hours():
    """Update structured opening hours for a shop."""
    try:
        data = request.json
        hours_json = json.dumps(data.get("hours", {}))
        
        shop = Shop.query.get_or_404(current_user.shop_id)
        shop.opening_hours = hours_json
        db.session.commit()
        
        return Response(json.dumps({"success": True}), status=200, mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype="application/json")


@bp.route("/sitemap.xml")
def sitemap():
    """Dynamically generated sitemap."""
    shops_query = Shop.query.all()
    shops = []
    for shop in shops_query:
        shops.append({
            "id": shop.id,
            "slug": shop.slug
        })
    xml = generate_sitemap_xml(shops, base_url=BASE_URL)
    return Response(xml, mimetype="application/xml")


@bp.route("/robots.txt")
def robots():
    """Serve robots.txt."""
    return bp.send_static_file("robots.txt")


# ── Error handlers ───────────────────────────────────────────────────────────

@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@bp.app_errorhandler(403)
def forbidden(e):
    return render_template("404.html"), 403
