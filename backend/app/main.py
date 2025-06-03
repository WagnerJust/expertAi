from fastapi import FastAPI
from app.apis.v1 import router_collections, router_pdfs
from app.db.session import init_db, SessionLocal
from app.utils.initial_corpus_ingest import ingest_initial_corpus

app = FastAPI()

@app.on_event("startup")
def on_startup():
    print("[startup] Startup event begins.")
    init_db()
    print("[startup] DB initialized.")
    db = SessionLocal()
    try:
        ingest_initial_corpus(db)
        print("[startup] Initial corpus ingested.")
    finally:
        db.close()

app.include_router(router_collections)
app.include_router(router_pdfs)

@app.get("/")
def health_check():
    return {"status": "ok"}
