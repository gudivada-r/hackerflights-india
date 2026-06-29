from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field
from datetime import datetime

class Hop(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    origin_iata: str = Field(index=True)
    destination_iata: str = Field(index=True)
    carrier: str
    carrier_code: str
    leg: str
    typical_price_usd: float
    avg_duration_hrs: float
    frequency: str = "daily"
    booking_url: Optional[str] = None
    notes: Optional[str] = None

class SearchLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    raw_query: str
    parsed_json: str
    result_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ParseRequest(SQLModel):
    query: str

class ParsedIntent(SQLModel):
    departure: Dict[str, Any]
    destination: Dict[str, Any]
    trip_type: str
    dates: Dict[str, Any]
    duration: Dict[str, Any]
    tags: List[str]

class HopResult(SQLModel):
    legs: List[Dict[str, Any]]
    total_price_usd: float
    total_duration_hrs: float
    relay_airports: List[str]
    score: float

class SearchResponse(SQLModel):
    query: str
    parsed_intent: Dict[str, Any]
    chains: List[HopResult]
