# ✈️ HackerFlights India

> USA → India for under $500 by chaining separate LCC tickets

HackerFlights finds cheap routes from the USA to India by **stringing together budget carrier tickets** across three legs:

```
USA Hub  →  European Hub  →  Gulf Hub  →  Indian City
(Norse / FrenchBee)  (Wizz / flydubai)  (IndiGo / AIX)
```

---

## Architecture

```
React Native (Expo)  ←→  FastAPI (Python)  ←→  SQLite
                              ↕
                     Mistral Nemo 12B (NLP)
                     (Ollama local or Mistral API)
```

---

## Project Structure

```
FLIGHT/
├── backend/                    # FastAPI backend
│   ├── main.py                 # App entry point
│   ├── models.py               # SQLModel tables & schemas
│   ├── database.py             # SQLite engine
│   ├── engine/
│   │   ├── mistral_client.py   # Ollama / Mistral API client
│   │   ├── solver.py           # 3-leg hop-chain routing engine
│   │   └── prompts/
│   │       └── intent_parser.txt  # Mistral Nemo system prompt
│   ├── routes/
│   │   ├── parse.py            # POST /parse
│   │   ├── search.py           # POST /search
│   │   └── hops.py             # GET /hops
│   ├── seed/
│   │   └── seed_hops.py        # Static LCC hop seed data (40 routes)
│   ├── tests/
│   │   └── test_solver.py      # pytest unit tests
│   ├── requirements.txt
│   └── .env.example
│
├── mobile/                     # React Native (Expo) mobile app
│   ├── app/
│   │   ├── _layout.tsx         # Root layout (fonts, status bar)
│   │   └── (tabs)/
│   │       ├── _layout.tsx     # Tab bar layout
│   │       ├── index.tsx       # Home / Search screen
│   │       ├── results.tsx     # Hop chain results screen
│   │       ├── saved.tsx       # Saved routes (AsyncStorage)
│   │       └── about.tsx       # How it works
│   ├── components/
│   │   ├── SearchBar.tsx       # Animated NL search input
│   │   ├── HopChainCard.tsx    # Result card with booking links
│   │   └── FlightPath.tsx      # Visual airport path display
│   ├── constants/
│   │   └── theme.ts            # Colors, fonts, spacing
│   └── services/
│       └── api.ts              # FastAPI client
│
└── README.md
```

---

## Backend Setup

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com) (for local Mistral Nemo inference)

### 1. Install dependencies
```powershell
pip install -r backend/requirements.txt
```

### 2. Configure environment
```powershell
Copy-Item backend\.env.example backend\.env
```

Edit `backend/.env`:
```env
MISTRAL_BACKEND=ollama          # or "api" for Mistral cloud
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral-nemo
MISTRAL_API_KEY=your_key_here   # only needed if MISTRAL_BACKEND=api
```

### 3. Pull Mistral Nemo (Ollama only)
```powershell
ollama pull mistral-nemo
```

### 4. Start the API server
```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

The server will **auto-seed** the SQLite database on startup.

Visit **http://127.0.0.1:8000/docs** for the interactive Swagger UI.

### 5. Run tests
```powershell
python -m pytest backend/tests/ -v
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/parse` | Parse plain-English query with Mistral Nemo |
| `POST` | `/search` | Full pipeline: NLP → solver → ranked chains |
| `GET`  | `/hops` | View all seeded LCC hops |
| `GET`  | `/health` | Health check |

### Example search request
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "cheapest flight from JFK to Bangalore next month"}'
```

---

## Mobile App Setup

### Prerequisites
- Node.js 18+
- [Expo Go](https://expo.dev/go) app on your phone (or Android/iOS emulator)

### 1. Install dependencies
```powershell
cd mobile
npm install
```

### 2. Configure API URL (optional)
In `mobile/app.json`, add:
```json
{
  "expo": {
    "extra": {
      "apiUrl": "http://YOUR_PC_IP:8000"
    }
  }
}
```
> ⚠️ Use your machine's local IP (not `localhost`) when testing on a physical device.

### 3. Start the app
```powershell
cd mobile
npx expo start
```

Scan the QR code with Expo Go on your phone.

---

## LCC Hop Map

### Leg 1: USA → Europe
| Carrier | Routes | ~Price |
|---------|--------|--------|
| Norse Atlantic | JFK/LAX/ORD → LGW | $250–$290 |
| FrenchBee | SFO/EWR/MIA → CDG | $230–$260 |
| Condor | JFK/LAX/SEA → FRA | $280–$320 |
| Icelandair | BOS/IAD → KEF | $180–$190 |

### Leg 2: Europe → Gulf
| Carrier | Routes | ~Price |
|---------|--------|--------|
| Wizz Air | LGW/CDG/FRA → DXB/AUH | $79–$90 |
| flydubai | LGW/CDG → DXB | $95–$100 |
| Air Arabia | LGW/CDG → SHJ | $75–$78 |

### Leg 3: Gulf → India
| Carrier | Routes | ~Price |
|---------|--------|--------|
| IndiGo | DXB → BLR/BOM/DEL/MAA/HYD/COK/GOI/CCU | $75–$98 |
| Air India Express | AUH → BLR/COK/MAA/BOM/DEL/GOI/HYD | $70–$85 |
| SpiceJet | DXB → AMD, SHJ → BLR/COK/MAA | $60–$72 |

**Example cheapest chain:** SFO → CDG (FrenchBee $230) + CDG → SHJ (Air Arabia $78) + SHJ → COK (SpiceJet $60) = **$368 total**

---

## ⚠️ Risk Disclaimer

These are **separate tickets** on different carriers. There is **no interline agreement**:
- No checked baggage transfer between carriers
- If one leg is delayed, other tickets are NOT reprotected
- Allow **minimum 8 hours** between legs at each relay airport
- **Buy travel insurance** that covers missed connections
- Prices are estimates — verify before booking

---

## Roadmap

| Phase | Feature |
|-------|---------|
| ✅ Phase 1 | NLP search, hop-chain solver, Expo mobile app |
| 🔄 Phase 2 | Live price polling (Amadeus/Kiwi), price history charts |
| 📋 Phase 3 | User accounts, saved watchlists, push price alerts |
