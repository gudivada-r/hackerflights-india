from typing import List, Dict, Any
from sqlmodel import Session, select
from backend.models import Hop, HopResult

TAG_DEST_MAP = {
    "warm_beach": ["GOI", "COK", "TRV", "MAA"],
    "tropical":   ["GOI", "COK", "TRV", "CCJ"],
    "nature":     ["IXZ", "GOI", "IXB"],
    "culture":    ["DEL", "CCU", "VAR", "BOM"],
    "city_break": ["BOM", "DEL", "BLR", "HYD"],
    "business_friendly": ["BLR", "HYD", "BOM", "DEL"],
}

ALL_INDIA_HUBS = ["BLR", "BOM", "DEL", "MAA", "HYD", "COK", "GOI", "CCU", "AMD"]
ALL_US_HUBS = ["JFK", "EWR", "LAX", "SFO", "ORD", "IAD", "BOS", "ATL", "MIA", "SEA"]
MIN_LAYOVER_HRS = 8.0
MAX_RESULTS = 10

def _get_candidate_destinations(intent: Dict[str, Any]) -> List[str]:
    dest = intent.get("destination", {})
    if dest.get("airport_code"):
        return [dest["airport_code"]]
    candidates = set()
    for tag in intent.get("tags", []):
        if tag in TAG_DEST_MAP:
            candidates.update(TAG_DEST_MAP[tag])
    return list(candidates) if candidates else ALL_INDIA_HUBS

def _get_candidate_origins(intent: Dict[str, Any]) -> List[str]:
    dep = intent.get("departure", {})
    if dep.get("airport_code"):
        return [dep["airport_code"]]
    return ALL_US_HUBS

def solve(intent: Dict[str, Any], session: Session) -> List[HopResult]:
    origins = _get_candidate_origins(intent)
    destinations = _get_candidate_destinations(intent)
    tags = intent.get("tags", [])

    usa_europe = session.exec(select(Hop).where(Hop.leg == "usa_europe")).all()
    europe_mideast = session.exec(select(Hop).where(Hop.leg == "europe_mideast")).all()
    mideast_india = session.exec(select(Hop).where(Hop.leg == "mideast_india")).all()

    chains: List[HopResult] = []

    for leg1 in usa_europe:
        if leg1.origin_iata not in origins:
            continue
        for leg2 in europe_mideast:
            if leg2.origin_iata != leg1.destination_iata:
                continue
            for leg3 in mideast_india:
                if leg3.origin_iata != leg2.destination_iata:
                    continue
                if leg3.destination_iata not in destinations:
                    continue

                total_price = leg1.typical_price_usd + leg2.typical_price_usd + leg3.typical_price_usd
                total_duration = (
                    leg1.avg_duration_hrs + MIN_LAYOVER_HRS +
                    leg2.avg_duration_hrs + MIN_LAYOVER_HRS +
                    leg3.avg_duration_hrs
                )
                chains.append(HopResult(
                    legs=[
                        {"origin": leg1.origin_iata, "destination": leg1.destination_iata,
                         "carrier": leg1.carrier, "carrier_code": leg1.carrier_code,
                         "price_usd": leg1.typical_price_usd, "duration_hrs": leg1.avg_duration_hrs,
                         "booking_url": leg1.booking_url},
                        {"origin": leg2.origin_iata, "destination": leg2.destination_iata,
                         "carrier": leg2.carrier, "carrier_code": leg2.carrier_code,
                         "price_usd": leg2.typical_price_usd, "duration_hrs": leg2.avg_duration_hrs,
                         "booking_url": leg2.booking_url},
                        {"origin": leg3.origin_iata, "destination": leg3.destination_iata,
                         "carrier": leg3.carrier, "carrier_code": leg3.carrier_code,
                         "price_usd": leg3.typical_price_usd, "duration_hrs": leg3.avg_duration_hrs,
                         "booking_url": leg3.booking_url},
                    ],
                    total_price_usd=round(total_price, 2),
                    total_duration_hrs=round(total_duration, 1),
                    relay_airports=[leg1.destination_iata, leg2.destination_iata],
                    score=0.0
                ))

    if not chains:
        return []

    max_p = max(c.total_price_usd for c in chains)
    max_d = max(c.total_duration_hrs for c in chains)
    w_price = 0.8 if "budget_priority" in tags else 0.7
    for c in chains:
        norm_p = c.total_price_usd / max_p if max_p else 0
        norm_d = c.total_duration_hrs / max_d if max_d else 0
        c.score = round(w_price * norm_p + (1 - w_price) * norm_d, 4)

    chains.sort(key=lambda c: c.score)
    return chains[:MAX_RESULTS]
