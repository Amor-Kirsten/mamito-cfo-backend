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
