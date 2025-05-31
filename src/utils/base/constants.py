"""
This file contains Global constants
Also storing all the env and config variables here
"""

from src.utils.base.libraries import os

# environment Constants (Fetching from docker-compose)
POSTGRES_DB_USERNAME = os.environ.get("POSTGRES_DB_USERNAME", "neko_nik")
POSTGRES_DB_PASSWORD = os.environ.get("POSTGRES_DB_PASSWORD", "NekoNik_com")
POSTGRES_DB_HOST = os.environ.get("POSTGRES_DB_HOST", "localhost")
POSTGRES_DB_PORT = os.environ.get("POSTGRES_DB_PORT", "5432")
POSTGRES_DB_DATABASE = os.environ.get("POSTGRES_DB_DATABASE", "neko_nik_db")
POSTGRES_POOL_SIZE = int(os.environ.get("POSTGRES_POOL_SIZE", 10))
POSTGRES_DB_URI = os.environ.get("POSTGRES_URI", f"postgresql://{POSTGRES_DB_USERNAME}:{POSTGRES_DB_PASSWORD}@{POSTGRES_DB_HOST}:{POSTGRES_DB_PORT}/{POSTGRES_DB_DATABASE}")

HCAPTCHA_SECRET_KEY = os.environ.get("HCAPTCHA_SECRET_KEY", "SOME_HCAPTCHA_SECRET_KEY")

# MemCache DB Constants
MEMCACHED_DB_HOST = os.environ.get("MEMCACHED_DB_HOST", "localhost")
MEMCACHED_DB_PORT = os.environ.get("MEMCACHED_DB_PORT", "11211")
MEMCACHED_DB_POOL_SIZE = int(os.environ.get("MEMCACHED_DB_POOL_SIZE", 10))
MAX_AGE_OF_CACHE = int(os.environ.get("MAX_AGE_OF_CACHE", 3*60*60)) # 3 hours


# log variables
LOG_LEVEL = int(os.environ.get("LOG_LEVEL", 20))
LOG_FILE_PATH = "/var/log/api/logs.jsonl"
