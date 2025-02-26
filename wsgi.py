from app import app
import os

if __name__ == "__main__":
    # This code runs when the script is executed directly
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
else:
    # This is what Gunicorn uses
    # The application variable is what Gunicorn looks for
    application = app 