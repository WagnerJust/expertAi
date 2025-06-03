from fastapi import FastAPI
from app.apis.v1 import router_collections, router_pdfs
from app.utils.initial_corpus_ingest import register_startup_event

app = FastAPI()
app.include_router(router_collections)
app.include_router(router_pdfs)
register_startup_event(app)

@app.get("/")
def health_check():
    return {"status": "ok"}
