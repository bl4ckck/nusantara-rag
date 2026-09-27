from fastapi import APIRouter
from fastapi.responses import JSONResponse

from rag import service, store
from .schemas import AskRequest, AskResponse

router = APIRouter()


@router.get("/health")
def health():
    try:
        return {"ok": True, "chunks": store.collection().count(),
                "collection": store.COLLECTION}
    except Exception:
        return JSONResponse({"ok": False, "error": "store unavailable"}, status_code=503)


@router.post("/seed")
def reseed():
    try:
        return store.seed()
    except Exception:
        return JSONResponse({"ok": False, "error": "store unavailable"}, status_code=503)


@router.post("/ask", response_model=AskResponse)
def ask(body: AskRequest):
    return service.answer(body.question.strip())
