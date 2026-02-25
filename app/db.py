"""Database connection and initialization helpers for Aura."""

import psycopg2
import psycopg2.extras
from flask import current_app, g


def get_db():
    """Return a database connection, creating one if needed."""
    if "db" not in g:
        g.db = psycopg2.connect(current_app.config["DATABASE_URL"])
        g.db.autocommit = True
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Create tables if they don't exist."""
    with app.app_context():
        try:
            conn = psycopg2.connect(app.config["DATABASE_URL"])
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS shops (
                    id              SERIAL PRIMARY KEY,
                    name            VARCHAR(200) NOT NULL,
                    slug            VARCHAR(200) UNIQUE NOT NULL,
                    description     TEXT,
                    address         TEXT,
                    city            VARCHAR(100),
                    province        VARCHAR(100),
                    postal_code     VARCHAR(10),
                    phone           VARCHAR(20),
                    latitude        DOUBLE PRECISION,
                    longitude       DOUBLE PRECISION,
                    opening_hours   VARCHAR(100),
                    image_url       VARCHAR(500),
                    is_delivery     BOOLEAN DEFAULT FALSE,
                    created_at      TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS products (
                    id              SERIAL PRIMARY KEY,
                    shop_id         INTEGER REFERENCES shops(id) ON DELETE CASCADE,
                    name            VARCHAR(200) NOT NULL,
                    price           NUMERIC(10,2) NOT NULL,
                    category        VARCHAR(100),
                    in_stock        BOOLEAN DEFAULT TRUE
                );

                CREATE TABLE IF NOT EXISTS orders (
                    id              SERIAL PRIMARY KEY,
                    shop_id         INTEGER REFERENCES shops(id) ON DELETE CASCADE,
                    customer_name   VARCHAR(200),
                    customer_phone  VARCHAR(20),
                    status          VARCHAR(50) DEFAULT 'pending',
                    total           NUMERIC(10,2),
                    created_at      TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS users (
                    id              SERIAL PRIMARY KEY,
                    shop_id         INTEGER REFERENCES shops(id) ON DELETE CASCADE,
                    email           VARCHAR(200) UNIQUE NOT NULL,
                    password_hash   VARCHAR(500) NOT NULL,
                    created_at      TIMESTAMP DEFAULT NOW()
                );

                -- Migration: Ensure missing columns exist in shops
                ALTER TABLE shops ADD COLUMN IF NOT EXISTS address TEXT;
                ALTER TABLE shops ADD COLUMN IF NOT EXISTS city VARCHAR(100);
                ALTER TABLE shops ADD COLUMN IF NOT EXISTS province VARCHAR(100);
                ALTER TABLE shops ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
                ALTER TABLE shops ALTER COLUMN opening_hours TYPE TEXT;
                ALTER TABLE shops ADD COLUMN IF NOT EXISTS opening_hours TEXT; -- In case it didn't exist at all

                -- Migration: Ensure missing columns exist in users
                ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);
                ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);
                ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

                -- Migration: Ensure product archiving and images support
                ALTER TABLE products ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE;
                ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url VARCHAR(500);
                """
            )
            cur.close()
            conn.close()
        except Exception as e:
            print(f"[Aura] DB init skipped or failed: {e}")
