#!/usr/bin/env python3
"""
DEPRECATED: This file was for SQLite migrations and is no longer needed.
The application now uses PostgreSQL with automatic schema management via SQLAlchemy.

For PostgreSQL migration, use:
- backend/migrate_to_postgres.py
- backend/app/migrate_to_postgres.py  
- backend/db_manager.py

This file is kept for reference but should not be used.
"""

import sys

def migrate_database():
    """DEPRECATED: No longer used - PostgreSQL handles schema automatically"""
    print("❌ This migration script is deprecated.")
    print("📚 The application now uses PostgreSQL with automatic schema management.")
    print("🔧 Use 'python db_manager.py init' instead to initialize PostgreSQL schema.")
    return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting database migration...")
        
        # 1. Add missing columns to collections table
        print("1. Updating collections table...")
        try:
            cursor.execute("ALTER TABLE collections ADD COLUMN description TEXT;")
            print("   - Added description column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   - description column already exists")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE collections ADD COLUMN updated_at DATETIME;")
            print("   - Added updated_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   - updated_at column already exists")
            else:
                raise
        
        # Set default updated_at for existing records
        cursor.execute("UPDATE collections SET updated_at = created_at WHERE updated_at IS NULL;")
        
        # 2. Add missing columns to pdf_documents table
        print("2. Updating pdf_documents table...")
        try:
            cursor.execute("ALTER TABLE pdf_documents ADD COLUMN file_path TEXT;")
            print("   - Added file_path column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   - file_path column already exists")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE pdf_documents ADD COLUMN created_at DATETIME;")
            print("   - Added created_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   - created_at column already exists")
            else:
                raise
                
        try:
            cursor.execute("ALTER TABLE pdf_documents ADD COLUMN updated_at DATETIME;")
            print("   - Added updated_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   - updated_at column already exists")
            else:
                raise
        
        # Set default timestamps for existing records
        current_time = datetime.utcnow().isoformat()
        cursor.execute("UPDATE pdf_documents SET created_at = ?, updated_at = ? WHERE created_at IS NULL;", (current_time, current_time))
        
        # 3. Update query_history table structure
        print("3. Updating query_history table...")
        
        # Check current column structure
        cursor.execute("PRAGMA table_info(query_history);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # SQLite doesn't support renaming columns easily, so we'll create a new table and migrate data
        if 'question_text' not in column_names:
            print("   - Migrating query_history table structure...")
            
            # Create new table with updated structure
            cursor.execute("""
                CREATE TABLE query_history_new (
                    id INTEGER PRIMARY KEY,
                    question_text TEXT NOT NULL,
                    answer_text TEXT,
                    sources_count INTEGER DEFAULT 0,
                    collection_id INTEGER,
                    timestamp DATETIME,
                    FOREIGN KEY (collection_id) REFERENCES collections (id)
                );
            """)
            
            # Migrate data from old table
            cursor.execute("""
                INSERT INTO query_history_new (id, question_text, collection_id, timestamp)
                SELECT id, text, collection_id, timestamp
                FROM query_history;
            """)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE query_history;")
            cursor.execute("ALTER TABLE query_history_new RENAME TO query_history;")
            
            print("   - Migrated query_history table successfully")
        else:
            print("   - query_history table already has correct structure")
            
            # Add missing columns if they don't exist
            if 'answer_text' not in column_names:
                cursor.execute("ALTER TABLE query_history ADD COLUMN answer_text TEXT;")
                print("   - Added answer_text column")
            
            if 'sources_count' not in column_names:
                cursor.execute("ALTER TABLE query_history ADD COLUMN sources_count INTEGER DEFAULT 0;")
                print("   - Added sources_count column")
        
        # 4. Update relationships in Answer table
        print("4. Checking Answer table relationships...")
        cursor.execute("PRAGMA table_info(answers);")
        answer_columns = cursor.fetchall()
        
        # Add back_populates relationship if it doesn't exist (SQLAlchemy will handle this)
        print("   - Answer table relationships will be handled by SQLAlchemy")
        
        # Commit all changes
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        
        # Verify the migration
        print("\nVerifying migration:")
        cursor.execute("PRAGMA table_info(collections);")
        collections_cols = [col[1] for col in cursor.fetchall()]
        print(f"Collections columns: {collections_cols}")
        
        cursor.execute("PRAGMA table_info(pdf_documents);")
        pdf_cols = [col[1] for col in cursor.fetchall()]
        print(f"PDF documents columns: {pdf_cols}")
        
if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
