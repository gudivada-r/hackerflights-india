import json
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from backend.database import get_session
from backend.models import ParseRequest, SearchLog, SearchResponse
from backend.engine.mistral_client import parse_intent
from backend.engine.solver import solve

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("", response_model=SearchResponse)
async def search(req: ParseRequest, session: Session = Depends(get_session)):
    """Full pipeline: NL query -> Mistral parse -> hop solver -> ranked chains."""
    try:
        intent = await parse_intent(req.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLP parsing failed: {str(e)}")

    chains = solve(intent, session)

    log = SearchLog(
        raw_query=req.query,
        parsed_json=json.dumps(intent),
        result_count=len(chains)
    )
    session.add(log)
    session.commit()

    return SearchResponse(query=req.query, parsed_intent=intent, chains=chains)
