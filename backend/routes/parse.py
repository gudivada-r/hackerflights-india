from fastapi import APIRouter, HTTPException
from backend.models import ParseRequest
from backend.engine.mistral_client import parse_intent

router = APIRouter(prefix="/parse", tags=["NLP"])

@router.post("")
async def parse_query(req: ParseRequest):
    """Parse a plain-English flight query into structured JSON using Mistral Nemo."""
    try:
        result = await parse_intent(req.query)
        return {"query": req.query, "parsed": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLP parsing failed: {str(e)}")
