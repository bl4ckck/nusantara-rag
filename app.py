from fastapi import FastAPI

from routes.rag import router as rag_router

app = FastAPI(title="NusantaraCare RAG")
app.include_router(rag_router)
