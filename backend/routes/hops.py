from fastapi import APIRouter, Depends
from typing import Optional, List
from sqlmodel import Session, select
from backend.database import get_session
from backend.models import Hop

router = APIRouter(prefix="/hops", tags=["Hops"])

@router.get("", response_model=List[Hop])
def get_hops(leg: Optional[str] = None, session: Session = Depends(get_session)):
    """Return all seeded hops, optionally filtered by leg type."""
    query = select(Hop)
    if leg:
        query = query.where(Hop.leg == leg)
    return session.exec(query).all()
