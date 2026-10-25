import os

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ["DB_PASSWORD"],
    "database": os.environ.get("DB_NAME", "card"),
    "charset": "utf8mb4"
}

FLASK_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": True
}
