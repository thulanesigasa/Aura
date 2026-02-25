"""Entry point for the Aura application."""

from app import create_app
from app.db import init_db, close_db

app = create_app()

# Register teardown
app.teardown_appcontext(close_db)

# Initialise database tables
init_db(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
