#!/usr/bin/env python3
"""
Debug script to identify where the app startup is hanging
"""
import sys
import os
sys.path.append('/Users/justin/LLMS/App/backend')

print("🔍 Debugging App Startup")
print("=" * 40)

try:
    print("1. Importing FastAPI...")
    from fastapi import FastAPI
    print("   ✅ FastAPI imported")
    
    print("2. Importing CORS middleware...")
    from fastapi.middleware.cors import CORSMiddleware
    print("   ✅ CORS imported")
    
    print("3. Importing database session...")
    from app.db.session import init_db, SessionLocal
    print("   ✅ Database session imported")
    
    print("4. Importing routers...")
    from app.apis.v1 import router_collections, router_pdfs, router_qa
    print("   ✅ Routers imported")
    
    print("5. Importing initial corpus utility...")
    from app.utils.initial_corpus_ingest import ingest_initial_corpus
    print("   ✅ Initial corpus utility imported")
    
    print("6. Creating FastAPI app...")
    app = FastAPI(title="PDF RAG Q&A System", version="1.0.0")
    print("   ✅ FastAPI app created")
    
    print("7. Adding CORS middleware...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("   ✅ CORS middleware added")
    
    print("8. Adding routers...")
    app.include_router(router_collections)
    app.include_router(router_pdfs)
    app.include_router(router_qa)
    print("   ✅ Routers added")
    
    print("9. Testing database initialization...")
    init_db()
    print("   ✅ Database initialized")
    
    print("10. Testing session creation...")
    db = SessionLocal()
    db.close()
    print("   ✅ Session created and closed")
    
    print("\n" + "=" * 40)
    print("✅ All components loaded successfully!")
    
except Exception as e:
    print(f"❌ Error during startup: {e}")
    import traceback
    traceback.print_exc()
