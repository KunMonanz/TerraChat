from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_DATABASE_URL")

if not POSTGRES_URL:
    raise RuntimeError("POSTGRES_DATABASE_URL is not set in .env")

TORTOISE_ORM = {
    "connections": {
        "sqlite": "sqlite://local_terra.sqlite3",
        "postgres": POSTGRES_URL,
    },
    "apps": {
        "cloud_models": {
            "models": [
                "models.cloud.user_cloud",
                "aerich.models"
            ],
            "default_connection": "postgres",
        },
        "local_models": {
            "models": [
                "models.local.user_local"
            ],
            "default_connection": "sqlite",
        },
    },
}
