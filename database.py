import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

load_dotenv()

url = os.getenv("DATABASE_URL")
if url and url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

import urllib.parse
if url and "@" in url and "://" in url:
    try:
        scheme, rest = url.split("://", 1)
        creds, host_db = rest.rsplit("@", 1)
        user, pwd = creds.split(":", 1)
        safe_pwd = urllib.parse.quote(urllib.parse.unquote(pwd))
        url = f"{scheme}://{user}:{safe_pwd}@{host_db}"
    except Exception:
        pass

if not url:
    if os.getenv("VERCEL"):
        url = "sqlite:////tmp/sales.db"
    else:
        url = "sqlite:///./sales.db"

SQLALCHEMY_DATABASE_URL = url

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # Use NullPool for Serverless Postgres connections to prevent Supabase PgBouncer Exhaustion
    engine = create_engine(SQLALCHEMY_DATABASE_URL, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
