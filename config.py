from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("WEBSOCKET_BACKEND_LOCAL_SERVER_SECRET_KEY").encode()
LARAVEL_TOKEN = os.getenv("WEBSOCKET_BACKEND_LOCAL_SERVER_TOKEN")
LARAVEL_NOTIFY_URL = os.getenv("LARAVEL_NOTIFY_URL")


