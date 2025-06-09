from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.apis.v1.router_collections import router as collections_router
from app.apis.v1.router_pdfs import router as pdfs_router  
from app.apis.v1.router_qa import router as qa_router
from app.db.session import init_db, SessionLocal
from app.utils.initial_corpus_ingest import ingest_initial_corpus
import time
import psycopg2
from app.core.config import settings

app = FastAPI(title="PDF RAG Q&A System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def wait_for_postgres(max_retries=30, delay=2):
    """Wait for PostgreSQL to be ready before starting the application"""
    print("[startup] Waiting for PostgreSQL to be ready...")
    
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
            print("[startup] PostgreSQL is ready!")
            return True
        except psycopg2.OperationalError as e:
            print(f"[startup] Attempt {i+1}/{max_retries}: PostgreSQL not ready yet...")
            time.sleep(delay)
    
    print("[startup] PostgreSQL failed to become ready in time!")
    return False

@app.on_event("startup")
def on_startup():
    print("[startup] Startup event begins.")
    
    # Wait for PostgreSQL to be ready
    if not wait_for_postgres():
        print("[startup] Failed to connect to PostgreSQL!")
        return
    
    # Initialize database
    init_db()
    print("[startup] DB initialized.")
    
    # Create default collection if it doesn't exist
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
            print(f"[startup] Created default collection: {settings.default_collection_name}")
        else:
            print(f"[startup] Default collection already exists: {settings.default_collection_name}")
    finally:
        db.close()
    
    # Temporarily disable initial corpus ingestion for testing
    # db = SessionLocal()
    # try:
    #     ingest_initial_corpus(db)
    #     print("[startup] Initial corpus ingested.")
    # finally:
    #     db.close()

app.include_router(collections_router)
app.include_router(pdfs_router)
app.include_router(qa_router)

@app.get("/")
def health_check():
    return {"status": "ok"}
