
# This is the main file that starts the app.
# It sets up the database and runs the web server.


from datetime import datetime  # Used for dates and times
import os  # Used to access environment variables
from app import app, db  # Import the app and database from the app folder

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    # For Cloud Run, listen on $PORT and remove SSL context
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=True)