#!/usr/bin/env python3
"""
Database migration script from SQLite to PostgreSQL
Run this script to initialize the PostgreSQL database with the schema.
"""

import sys
import os
import time
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

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
            # Try to connect directly with psycopg2
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
            print(f"Attempt {i+1}/{max_retries}: PostgreSQL not ready yet... ({e})")
            time.sleep(delay)
    
    print("PostgreSQL failed to become ready in time!")
    return False

def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    try:
        # Connect to default postgres database to create our database
        conn = psycopg2.connect(
            host="postgres",
            port=5432,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database="postgres"  # Connect to default database
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (settings.postgres_db,)
        )
        
        if not cursor.fetchone():
            # Database doesn't exist, create it
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
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    
    return True

def initialize_schema():
    """Initialize the database schema"""
    try:
        print("Initializing database schema...")
        
        # Test connection first
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"Connected to PostgreSQL: {version}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database schema created successfully!")
        
        # Create default collection if it doesn't exist
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
        print(f"Error initializing schema: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main migration function"""
    print("Starting PostgreSQL database migration...")
    
    # Wait for PostgreSQL to be ready
    if not wait_for_postgres():
        print("Failed to connect to PostgreSQL")
        sys.exit(1)
    
    # Create database if needed
    if not create_database_if_not_exists():
        print("Failed to create database")
        sys.exit(1)
    
    # Initialize schema
    if not initialize_schema():
        print("Failed to initialize schema")
        sys.exit(1)
    
    print("PostgreSQL migration completed successfully!")

if __name__ == "__main__":
    main()
