from app import app
import os

# This is the application Gunicorn will use
application = app

if __name__ == "__main__":
    # This code runs when the script is executed directly
    port = int(os.environ.get("PORT", 8080))
    application.run(host="0.0.0.0", port=port)
else:
    # This is what Gunicorn uses
    # The application variable is what Gunicorn looks for
    application = app 