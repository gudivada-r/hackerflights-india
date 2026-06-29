"""
Run with: python -m backend.seed.seed_hops
Seeds the SQLite database with static LCC hop route data.
"""
from backend.database import init_db, engine
from backend.models import Hop
from sqlmodel import Session, select

HOPS = [
    # LEG 1: USA -> Europe
    {"origin_iata":"JFK","destination_iata":"LGW","carrier":"Norse Atlantic","carrier_code":"N0","leg":"usa_europe","typical_price_usd":250,"avg_duration_hrs":7.5,"frequency":"daily","booking_url":"https://flynorse.com"},
    {"origin_iata":"LAX","destination_iata":"LGW","carrier":"Norse Atlantic","carrier_code":"N0","leg":"usa_europe","typical_price_usd":290,"avg_duration_hrs":10.5,"frequency":"daily","booking_url":"https://flynorse.com"},
    {"origin_iata":"ORD","destination_iata":"LGW","carrier":"Norse Atlantic","carrier_code":"N0","leg":"usa_europe","typical_price_usd":270,"avg_duration_hrs":8.5,"frequency":"weekly","booking_url":"https://flynorse.com"},
    {"origin_iata":"SFO","destination_iata":"CDG","carrier":"FrenchBee","carrier_code":"BF","leg":"usa_europe","typical_price_usd":240,"avg_duration_hrs":11.0,"frequency":"daily","booking_url":"https://frenchbee.com"},
    {"origin_iata":"EWR","destination_iata":"CDG","carrier":"FrenchBee","carrier_code":"BF","leg":"usa_europe","typical_price_usd":230,"avg_duration_hrs":7.5,"frequency":"daily","booking_url":"https://frenchbee.com"},
    {"origin_iata":"MIA","destination_iata":"CDG","carrier":"FrenchBee","carrier_code":"BF","leg":"usa_europe","typical_price_usd":260,"avg_duration_hrs":9.5,"frequency":"weekly","booking_url":"https://frenchbee.com"},
    {"origin_iata":"JFK","destination_iata":"FRA","carrier":"Condor","carrier_code":"DE","leg":"usa_europe","typical_price_usd":280,"avg_duration_hrs":8.0,"frequency":"daily","booking_url":"https://condor.com"},
    {"origin_iata":"LAX","destination_iata":"FRA","carrier":"Condor","carrier_code":"DE","leg":"usa_europe","typical_price_usd":320,"avg_duration_hrs":11.5,"frequency":"daily","booking_url":"https://condor.com"},
    {"origin_iata":"SEA","destination_iata":"FRA","carrier":"Condor","carrier_code":"DE","leg":"usa_europe","typical_price_usd":300,"avg_duration_hrs":10.5,"frequency":"weekly","booking_url":"https://condor.com"},
    {"origin_iata":"BOS","destination_iata":"KEF","carrier":"Icelandair","carrier_code":"FI","leg":"usa_europe","typical_price_usd":180,"avg_duration_hrs":5.5,"frequency":"daily","booking_url":"https://icelandair.com"},
    {"origin_iata":"IAD","destination_iata":"KEF","carrier":"Icelandair","carrier_code":"FI","leg":"usa_europe","typical_price_usd":190,"avg_duration_hrs":6.5,"frequency":"daily","booking_url":"https://icelandair.com"},
    # LEG 2: Europe -> Middle East
    {"origin_iata":"LGW","destination_iata":"AUH","carrier":"Wizz Air","carrier_code":"W6","leg":"europe_mideast","typical_price_usd":80,"avg_duration_hrs":6.5,"frequency":"daily","booking_url":"https://wizzair.com"},
    {"origin_iata":"LGW","destination_iata":"DXB","carrier":"Wizz Air","carrier_code":"W6","leg":"europe_mideast","typical_price_usd":85,"avg_duration_hrs":6.5,"frequency":"daily","booking_url":"https://wizzair.com"},
    {"origin_iata":"CDG","destination_iata":"DXB","carrier":"Wizz Air","carrier_code":"W6","leg":"europe_mideast","typical_price_usd":90,"avg_duration_hrs":6.0,"frequency":"daily","booking_url":"https://wizzair.com"},
    {"origin_iata":"CDG","destination_iata":"AUH","carrier":"Wizz Air","carrier_code":"W6","leg":"europe_mideast","typical_price_usd":88,"avg_duration_hrs":6.2,"frequency":"daily","booking_url":"https://wizzair.com"},
    {"origin_iata":"FRA","destination_iata":"DXB","carrier":"Wizz Air","carrier_code":"W6","leg":"europe_mideast","typical_price_usd":82,"avg_duration_hrs":5.8,"frequency":"daily","booking_url":"https://wizzair.com"},
    {"origin_iata":"FRA","destination_iata":"AUH","carrier":"Wizz Air","carrier_code":"W6","leg":"europe_mideast","typical_price_usd":79,"avg_duration_hrs":6.0,"frequency":"daily","booking_url":"https://wizzair.com"},
    {"origin_iata":"LGW","destination_iata":"DXB","carrier":"flydubai","carrier_code":"FZ","leg":"europe_mideast","typical_price_usd":95,"avg_duration_hrs":6.5,"frequency":"daily","booking_url":"https://flydubai.com"},
    {"origin_iata":"CDG","destination_iata":"DXB","carrier":"flydubai","carrier_code":"FZ","leg":"europe_mideast","typical_price_usd":100,"avg_duration_hrs":6.0,"frequency":"daily","booking_url":"https://flydubai.com"},
    {"origin_iata":"LGW","destination_iata":"SHJ","carrier":"Air Arabia","carrier_code":"G9","leg":"europe_mideast","typical_price_usd":75,"avg_duration_hrs":6.8,"frequency":"weekly","booking_url":"https://airarabia.com"},
    {"origin_iata":"CDG","destination_iata":"SHJ","carrier":"Air Arabia","carrier_code":"G9","leg":"europe_mideast","typical_price_usd":78,"avg_duration_hrs":6.3,"frequency":"weekly","booking_url":"https://airarabia.com"},
    {"origin_iata":"KEF","destination_iata":"DXB","carrier":"Wizz Air","carrier_code":"W6","leg":"europe_mideast","typical_price_usd":120,"avg_duration_hrs":7.5,"frequency":"weekly","booking_url":"https://wizzair.com"},
    # LEG 3: Middle East -> India
    {"origin_iata":"DXB","destination_iata":"BLR","carrier":"IndiGo","carrier_code":"6E","leg":"mideast_india","typical_price_usd":90,"avg_duration_hrs":3.5,"frequency":"daily","booking_url":"https://goindigo.in"},
    {"origin_iata":"DXB","destination_iata":"BOM","carrier":"IndiGo","carrier_code":"6E","leg":"mideast_india","typical_price_usd":85,"avg_duration_hrs":3.0,"frequency":"daily","booking_url":"https://goindigo.in"},
    {"origin_iata":"DXB","destination_iata":"DEL","carrier":"IndiGo","carrier_code":"6E","leg":"mideast_india","typical_price_usd":88,"avg_duration_hrs":3.2,"frequency":"daily","booking_url":"https://goindigo.in"},
    {"origin_iata":"DXB","destination_iata":"MAA","carrier":"IndiGo","carrier_code":"6E","leg":"mideast_india","typical_price_usd":92,"avg_duration_hrs":3.8,"frequency":"daily","booking_url":"https://goindigo.in"},
    {"origin_iata":"DXB","destination_iata":"HYD","carrier":"IndiGo","carrier_code":"6E","leg":"mideast_india","typical_price_usd":89,"avg_duration_hrs":3.3,"frequency":"daily","booking_url":"https://goindigo.in"},
    {"origin_iata":"DXB","destination_iata":"COK","carrier":"IndiGo","carrier_code":"6E","leg":"mideast_india","typical_price_usd":75,"avg_duration_hrs":2.8,"frequency":"daily","booking_url":"https://goindigo.in"},
    {"origin_iata":"DXB","destination_iata":"GOI","carrier":"IndiGo","carrier_code":"6E","leg":"mideast_india","typical_price_usd":80,"avg_duration_hrs":3.0,"frequency":"daily","booking_url":"https://goindigo.in"},
    {"origin_iata":"DXB","destination_iata":"CCU","carrier":"IndiGo","carrier_code":"6E","leg":"mideast_india","typical_price_usd":98,"avg_duration_hrs":4.2,"frequency":"daily","booking_url":"https://goindigo.in"},
    {"origin_iata":"AUH","destination_iata":"BLR","carrier":"Air India Express","carrier_code":"IX","leg":"mideast_india","typical_price_usd":85,"avg_duration_hrs":3.5,"frequency":"daily","booking_url":"https://airindiaexpress.com"},
    {"origin_iata":"AUH","destination_iata":"COK","carrier":"Air India Express","carrier_code":"IX","leg":"mideast_india","typical_price_usd":70,"avg_duration_hrs":2.8,"frequency":"daily","booking_url":"https://airindiaexpress.com"},
    {"origin_iata":"AUH","destination_iata":"MAA","carrier":"Air India Express","carrier_code":"IX","leg":"mideast_india","typical_price_usd":80,"avg_duration_hrs":3.5,"frequency":"daily","booking_url":"https://airindiaexpress.com"},
    {"origin_iata":"AUH","destination_iata":"BOM","carrier":"Air India Express","carrier_code":"IX","leg":"mideast_india","typical_price_usd":78,"avg_duration_hrs":3.0,"frequency":"daily","booking_url":"https://airindiaexpress.com"},
    {"origin_iata":"AUH","destination_iata":"DEL","carrier":"Air India Express","carrier_code":"IX","leg":"mideast_india","typical_price_usd":82,"avg_duration_hrs":3.2,"frequency":"daily","booking_url":"https://airindiaexpress.com"},
    {"origin_iata":"AUH","destination_iata":"GOI","carrier":"Air India Express","carrier_code":"IX","leg":"mideast_india","typical_price_usd":75,"avg_duration_hrs":3.0,"frequency":"weekly","booking_url":"https://airindiaexpress.com"},
    {"origin_iata":"AUH","destination_iata":"HYD","carrier":"Air India Express","carrier_code":"IX","leg":"mideast_india","typical_price_usd":80,"avg_duration_hrs":3.3,"frequency":"daily","booking_url":"https://airindiaexpress.com"},
    {"origin_iata":"DXB","destination_iata":"AMD","carrier":"SpiceJet","carrier_code":"SG","leg":"mideast_india","typical_price_usd":72,"avg_duration_hrs":2.8,"frequency":"daily","booking_url":"https://spicejet.com"},
    {"origin_iata":"SHJ","destination_iata":"BLR","carrier":"SpiceJet","carrier_code":"SG","leg":"mideast_india","typical_price_usd":68,"avg_duration_hrs":3.2,"frequency":"weekly","booking_url":"https://spicejet.com"},
    {"origin_iata":"SHJ","destination_iata":"COK","carrier":"SpiceJet","carrier_code":"SG","leg":"mideast_india","typical_price_usd":60,"avg_duration_hrs":2.5,"frequency":"weekly","booking_url":"https://spicejet.com"},
    {"origin_iata":"SHJ","destination_iata":"MAA","carrier":"SpiceJet","carrier_code":"SG","leg":"mideast_india","typical_price_usd":65,"avg_duration_hrs":3.0,"frequency":"weekly","booking_url":"https://spicejet.com"},
]

def seed():
    init_db()
    with Session(engine) as session:
        existing = session.exec(select(Hop)).first()
        if existing:
            print("Database already seeded. Skipping.")
            return
        for hop_data in HOPS:
            session.add(Hop(**hop_data))
        session.commit()
        print(f"Seeded {len(HOPS)} hops into the database.")

if __name__ == "__main__":
    seed()
