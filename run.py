"""Entry point for the Aura application."""

from app import create_app
from app.db import init_db, seed_demo_data, close_db

app = create_app()

# Register teardown
app.teardown_appcontext(close_db)

# Initialise database tables and seed demo data
init_db(app)
seed_demo_data(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
