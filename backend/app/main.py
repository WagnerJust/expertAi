from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.apis.v1.router_collections import router as collections_router
from app.apis.v1.router_pdfs import router as pdfs_router  
from app.apis.v1.router_qa import router as qa_router
from app.db.session import init_db, SessionLocal
from app.utils.initial_corpus_ingest import ingest_initial_corpus

app = FastAPI(title="PDF RAG Q&A System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    print("[startup] Startup event begins.")
    init_db()
    print("[startup] DB initialized.")
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
