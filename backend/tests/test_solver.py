import pytest
from sqlmodel import SQLModel, Session, create_engine
from backend.models import Hop, HopResult
from backend.engine.solver import solve

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        hops = [
            Hop(origin_iata="JFK", destination_iata="LGW", carrier="Norse", carrier_code="N0",
                leg="usa_europe", typical_price_usd=250, avg_duration_hrs=7.5),
            Hop(origin_iata="LGW", destination_iata="DXB", carrier="Wizz Air", carrier_code="W6",
                leg="europe_mideast", typical_price_usd=80, avg_duration_hrs=6.5),
            Hop(origin_iata="DXB", destination_iata="BLR", carrier="IndiGo", carrier_code="6E",
                leg="mideast_india", typical_price_usd=90, avg_duration_hrs=3.5),
        ]
        for h in hops:
            s.add(h)
        s.commit()
        yield s

def test_basic_chain(session):
    intent = {
        "departure": {"airport_code": "JFK", "region": "USA"},
        "destination": {"airport_code": "BLR", "flexible_anywhere": False},
        "tags": [],
    }
    results = solve(intent, session)
    assert len(results) == 1
    assert results[0].total_price_usd == 420.0
    assert results[0].relay_airports == ["LGW", "DXB"]

def test_flexible_destination(session):
    intent = {
        "departure": {"airport_code": "JFK", "region": "USA"},
        "destination": {"airport_code": None, "flexible_anywhere": True},
        "tags": [],
    }
    results = solve(intent, session)
    assert len(results) >= 1

def test_budget_scoring(session):
    intent = {
        "departure": {"airport_code": "JFK"},
        "destination": {"airport_code": None, "flexible_anywhere": True},
        "tags": ["budget_priority"],
    }
    results = solve(intent, session)
    assert isinstance(results, list)
