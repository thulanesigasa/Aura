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
                """
            )
            cur.close()
            conn.close()
        except Exception as e:
            print(f"[Aura] DB init skipped or failed: {e}")


def seed_demo_data(app):
    """Insert demo shops if the table is empty."""
    with app.app_context():
        try:
            conn = psycopg2.connect(app.config["DATABASE_URL"])
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM shops;")
            count = cur.fetchone()[0]
            if count == 0:
                cur.execute(
                    """
                    INSERT INTO shops (name, slug, description, address, city, province, postal_code, phone, latitude, longitude, opening_hours, is_delivery)
                    VALUES
                        ('Mama Zinzi''s Spaza', 'mama-zinzis-spaza',
                         'Your trusted neighbourhood Spaza shop in Khayelitsha, stocking fresh bread, milk, snacks, airtime and everyday essentials.',
                         '14 Mew Way, Khayelitsha', 'Cape Town', 'Western Cape', '7784', '072 123 4567',
                         -34.0389, 18.6768, 'Mon-Sat 06:00-20:00', TRUE),
                        ('Uncle T''s Corner Store', 'uncle-ts-corner-store',
                         'Friendly corner store in Soweto offering cold drinks, toiletries, snacks and mobile money services.',
                         '88 Vilakazi St, Orlando West, Soweto', 'Johannesburg', 'Gauteng', '1804', '079 876 5432',
                         -26.2387, 27.9085, 'Mon-Sun 07:00-21:00', FALSE),
                        ('Siya''s Daily Needs', 'siyas-daily-needs',
                         'One-stop Spaza in Mamelodi for groceries, prepaid electricity, and household supplies.',
                         '23 Tsamaya Ave, Mamelodi East', 'Pretoria', 'Gauteng', '0122', '081 555 6789',
                         -25.7201, 28.3965, 'Mon-Fri 06:30-19:00, Sat 07:00-17:00', TRUE);
                    """
                )
                print("[Aura] Demo shops seeded.")
            cur.close()
            conn.close()
        except Exception as e:
            print(f"[Aura] Seed skipped or failed: {e}")
