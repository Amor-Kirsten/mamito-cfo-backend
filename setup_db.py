import os
from sqlalchemy import create_engine
import models

def init_db():
    print("🚀 Initializing Mamito Sales Database...\n")
    url = input("Please paste your Supabase Direct Connection URL (Port 5432):\n> ").strip()
    
    if not url:
        print("Error: No URL provided.")
        return
        
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        
    import urllib.parse
    if "@" in url and "://" in url:
        try:
            scheme, rest = url.split("://", 1)
            creds, host_db = rest.rsplit("@", 1)
            user, pwd = creds.split(":", 1)
            safe_pwd = urllib.parse.quote(urllib.parse.unquote(pwd))
            url = f"{scheme}://{user}:{safe_pwd}@{host_db}"
        except Exception:
            pass
            
    print("\nConnecting to database...")
    try:
        engine = create_engine(url)
        models.Base.metadata.create_all(bind=engine)
        print("✅ Database tables successfully created!")
        print("You can now securely use the app.")
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")

if __name__ == "__main__":
    init_db()
