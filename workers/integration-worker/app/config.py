import os

DB_USER = os.getenv("DB_USER", "janswasthya_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "janswasthya_pass")
DB_HOST = os.getenv("DB_HOST", "mariadb")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "janswasthya")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
PROVIDER_BASE_URL = os.getenv("PROVIDER_BASE_URL", "http://mock-provider-system:9000")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "3"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))