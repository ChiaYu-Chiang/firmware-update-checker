from waitress import serve
from app import app
import os

if __name__ == "__main__":
    # if use reverse proxy, set HOST to localhost
    host = os.environ.get("HOST", "0.0.0.0")
    serve(app, host=host, port=5001)
