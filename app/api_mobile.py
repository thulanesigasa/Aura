import jwt
import datetime
from flask import Blueprint, request, jsonify, current_app
from .models import Driver, User

# Prefixing the blueprint to isolate the new RESTful mobile API
api_mobile_bp = Blueprint("api_mobile", __name__, url_prefix="/api/v1/mobile")

def generate_jwt(identity, role):
    """Generate a JWT token valid for 30 days."""
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
        'iat': datetime.datetime.utcnow(),
        'sub': identity,
        'role': role
    }
    return jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )

@api_mobile_bp.route("/auth/login", methods=["POST"])
def mobile_login():
    """
    Mobile API Login endpoint.
    Expects JSON: {"email": "...", "password": "...", "role": "driver" | "admin"}
    Returns JSON with JWT token.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
        
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "driver") # Default to driver app login
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if role == "driver":
        user = Driver.query.filter_by(email=email).first()
    else:
        user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        # Admin MFA check could go here if role == 'admin'
        if role == "driver" and not getattr(user, 'is_active', True):
            return jsonify({"error": "Account is inactive"}), 403
            
        token = generate_jwt(user.id, role)
        return jsonify({
            "success": True,
            "token": token,
            "role": role,
            "user": {
                "id": user.id,
                "name": getattr(user, 'name', f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()),
                "shop_id": user.shop_id
            }
        }), 200
        
    return jsonify({"error": "Invalid credentials"}), 401
