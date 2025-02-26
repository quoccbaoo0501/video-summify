import os
from app import app

# For gunicorn, this is what it looks for
application = app

if __name__ == "__main__":
    # When running directly, use uvicorn
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
else:
    # This is what Gunicorn uses
    # The application variable is what Gunicorn looks for
    application = app 