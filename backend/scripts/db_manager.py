#!/usr/bin/env python3
"""
Database management utility for PostgreSQL migration and operations
"""

import sys
import os
import argparse
import time
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text
import subprocess

# Add the app directory to Python path
sys.path.append('/app')

from app.core.config import settings
from app.models.db_models import Base
from app.db.session import engine

def wait_for_postgres(max_retries=30, delay=2):
    """Wait for PostgreSQL to be ready"""
    print("Waiting for PostgreSQL to be ready...")
    
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host="postgres",
                port=5432,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db
            )
            conn.close()
            print("PostgreSQL is ready!")
            return True
        except psycopg2.OperationalError as e:
            print(f"Attempt {i+1}/{max_retries}: PostgreSQL not ready yet...")
            time.sleep(delay)
    
    print("PostgreSQL failed to become ready in time!")
    return False

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host="postgres",
            port=5432,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (settings.postgres_db,)
        )
        
        if not cursor.fetchone():
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(settings.postgres_db)
                )
            )
            print(f"Created database: {settings.postgres_db}")
        else:
            print(f"Database {settings.postgres_db} already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def init_schema():
    """Initialize the database schema"""
    try:
        print("Initializing database schema...")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"Connected to PostgreSQL: {version}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database schema created successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error initializing schema: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_default_collection():
    """Create the default collection"""
    try:
        from app.db.session import SessionLocal
        from app.models.db_models import Collection
        
        db = SessionLocal()
        try:
            default_collection = db.query(Collection).filter(
                Collection.name == settings.default_collection_name
            ).first()
            
            if not default_collection:
                default_collection = Collection(
                    name=settings.default_collection_name,
                    description="Default collection for documents"
                )
                db.add(default_collection)
                db.commit()
                print(f"Created default collection: {settings.default_collection_name}")
            else:
                print(f"Default collection already exists: {settings.default_collection_name}")
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"Error creating default collection: {e}")
        return False

def drop_database():
    """Drop the database (careful!)"""
    try:
        conn = psycopg2.connect(
            host="postgres",
            port=5432,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Terminate active connections to the database
        cursor.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s AND pid <> pg_backend_pid()
        """, (settings.postgres_db,))
        
        # Drop the database
        cursor.execute(
            sql.SQL("DROP DATABASE IF EXISTS {}").format(
                sql.Identifier(settings.postgres_db)
            )
        )
        print(f"Dropped database: {settings.postgres_db}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error dropping database: {e}")
        return False

def reset_database():
    """Reset the database (drop and recreate)"""
    print("Resetting database...")
    if drop_database() and create_database() and init_schema():
        create_default_collection()
        print("Database reset successfully!")
        return True
    return False

def show_status():
    """Show database connection status and basic info"""
    try:
        print("Database Status:")
        print("=" * 40)
        
        with engine.connect() as conn:
            # Get PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"PostgreSQL Version: {version.split(',')[0]}")
            
            # Get database name and size
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"Current Database: {db_name}")
            
            # List tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"Tables: {', '.join(tables) if tables else 'None'}")
            
            # Count collections
            if 'collections' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM collections"))
                count = result.fetchone()[0]
                print(f"Collections Count: {count}")
        
        print("✅ Database connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Database management utility")
    parser.add_argument("command", choices=[
        "init", "reset", "status", "create-db", "drop-db", "wait"
    ], help="Command to execute")
    
    args = parser.parse_args()
    
    if args.command == "wait":
        success = wait_for_postgres()
    elif args.command == "create-db":
        success = wait_for_postgres() and create_database()
    elif args.command == "init":
        success = (wait_for_postgres() and 
                  create_database() and 
                  init_schema() and 
                  create_default_collection())
    elif args.command == "reset":
        success = wait_for_postgres() and reset_database()
    elif args.command == "drop-db":
        success = wait_for_postgres() and drop_database()
    elif args.command == "status":
        success = show_status()
    else:
        print(f"Unknown command: {args.command}")
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
