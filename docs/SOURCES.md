# SOURCES.md — Research on Each Data Source

## For each source: what I researched, what I learned,
## what my sample data looks like, and what would break.

---

## 1. SAP — Fuel & Procurement Data

### What I Researched:
SAP exports data in multiple formats:
- IDoc (Intermediate Document) — EDI format, complex XML
- OData service — REST API, requires SAP Gateway
- BAPI — Remote Function Calls, requires SAP access
- Flat file / CSV — Manual export from SAP transactions
  (MB51, ME2M, S_ALR_87012093)

### What I Learned:
- Real SAP exports have German column headers in some configs
  (MENGE = quantity, WERKS = plant, MATNR = material)
- Plant codes (WERKS) mean nothing without a lookup table
- Dates come in DD.MM.YYYY format (German standard)
- Units are SAP internal codes (L = liters, M3 = cubic meters)
- Same material can have different units across plants
- Procurement data mixes fuel with non-fuel materials

### Why I Chose Flat File CSV:
Most sustainability teams receive SAP exports via email
or SFTP as CSV files. They don't have direct SAP API
access. Flat file is the most realistic ingestion path
for a prototype.

### My Sample Data:
```csv
PLANT,MATERIAL,QUANTITY,UNIT,POSTING_DATE,COST_CENTER,FUEL_TYPE
P001,DIESEL,500,L,01.03.2026,CC001,Diesel
P001,PETROL,200,L,02.03.2026,CC001,Petrol
P002,DIESEL,750,L,03.03.2026,CC002,Diesel
P002,NATURAL_GAS,100,M3,04.03.2026,CC002,Natural Gas
P003,DIESEL,300,L,05.03.2026,CC003,Diesel
```

**Why it looks this way:**
- PLANT codes reflect real SAP plant structure
- UNIT uses SAP standard codes (L, M3)
- COST_CENTER reflects real SAP organizational structure
- Multiple fuel types across plants — realistic for
  a manufacturing company with multiple locations

### What Would Break in Real Deployment:
1. German column headers — MENGE instead of QUANTITY
2. Date format — 01.03.2026 instead of 2026-03-01
3. Non-fuel materials mixed in — need material type filter
4. Plant codes need lookup table for human-readable names
5. Encoding issues — SAP exports often in ISO-8859-1
6. Large files — 100k+ rows common for annual exports

---

## 2. Utility Data — Electricity

### What I Researched:
Utility data comes in multiple ways:
- Portal CSV export (BSES, Adani, BESCOM, Tata Power)
- PDF bills (most common but hard to parse)
- Green Button API (US standard, not common in India)
- Manual entry from paper bills

### What I Learned:
- Billing periods don't align with calendar months
  (e.g., 15 Jan to 14 Feb)
- Multiple meters per site are common
- Units vary: kWh, MWh, kVAh
- Tariff structures vary: ToD (Time of Day), flat rate
- Some bills show estimated vs actual readings
- Large commercial clients have separate demand charges
- Indian utilities: BSES (Delhi), Adani (Mumbai/Gujarat),
  BESCOM (Bangalore), Tata Power

### Why I Chose Portal CSV Export:
Most utility portals in India offer CSV download.
PDF parsing requires OCR which adds complexity.
CSV is what a facilities manager actually downloads
at month end.

### My Sample Data:
```csv
METER_ID,SITE_NAME,BILLING_PERIOD_START,BILLING_PERIOD_END,
KWH_CONSUMED,TARIFF_RATE,CURRENCY,SUPPLIER
M001,Delhi Office,01-01-2026,31-01-2026,4500,8.50,INR,BSES
M001,Delhi Office,01-02-2026,28-02-2026,4200,8.50,INR,BSES
M002,Mumbai Office,15-01-2026,14-02-2026,6800,9.20,INR,Adani
M002,Mumbai Office,15-02-2026,14-03-2026,7100,9.20,INR,Adani
M003,Bangalore Office,01-01-2026,31-01-2026,3900,7.80,INR,BESCOM
```

**Why it looks this way:**
- Multiple meters (M001, M002, M003) — realistic for
  a company with offices in multiple cities
- Billing periods don't align (M002 starts 15th) —
  this is real utility billing behavior
- Different tariff rates per city — BSES vs Adani vs BESCOM
- Real Indian utility suppliers used

### What Would Break in Real Deployment:
1. PDF bills — no CSV export available from some utilities
2. MWh vs kWh — unit conversion needed
3. Estimated readings — marked differently in portal
4. Time-of-Day tariffs — billing period splits by time
5. Multiple meters aggregated on one bill
6. Power factor corrections in bill amount

---

## 3. Corporate Travel — Flights, Hotels, Ground

### What I Researched:
Travel platforms that expose data:
- Concur (SAP) — most common enterprise travel platform
- Navan (formerly TripActions) — newer, API-first
- AmEx GBT — American Express Global Business Travel
- Manual expense reports — Excel/CSV

Concur API exposes:
- Travel requests (/travelrequest/v4/requests)
- Expense reports (/expensereports/v3.0/reports)
- Trip data (/travel/v1/trips)

### What I Learned:
- Distances are NOT always provided — only origin/destination
- Airport codes (IATA) used — DEL, BOM, BLR
- Need distance lookup (Haversine formula or API)
- Hotel stays tracked separately from flights
- Ground transport often missing or incomplete
- Cabin class matters — business = 2.7x economy emissions
- Some platforms give CO2 estimates, some don't
- Concur requires OAuth 2.0 for API access

### Why I Chose JSON Export:
Travel data has multiple record types (flight/hotel/ground)
each with different fields. JSON handles this naturally.
CSV would require many empty columns per row type.
Concur and Navan both support JSON export format.

### My Sample Data:
```json
[
  {
    "employee_id": "E001",
    "travel_type": "flight",
    "origin": "DEL",
    "destination": "BOM",
    "travel_date": "2026-01-15",
    "distance_km": 1400,
    "cabin_class": "economy",
    "cost": 8500
  },
  {
    "employee_id": "E002",
    "travel_type": "hotel",
    "city": "Mumbai",
    "check_in": "2026-01-15",
    "check_out": "2026-01-17",
    "nights": 2,
    "cost": 6000
  },
  {
    "employee_id": "E001",
    "travel_type": "ground",
    "origin": "BOM Airport",
    "destination": "BOM Office",
    "distance_km": 35,
    "mode": "taxi",
    "cost": 850
  }
]
```

**Why it looks this way:**
- IATA airport codes (DEL, BOM, BLR) — real codes
- Distance pre-calculated — realistic for Concur export
- Mixed travel types in one file — real Concur behavior
- INR costs — India-based company
- Economy vs business cabin — different emission factors

### What Would Break in Real Deployment:
1. Distance not provided — need IATA distance API
2. OAuth authentication for Concur API
3. Pagination — large companies have 1000s of trips
4. Currency conversion — international travel in USD
5. Personal vs business travel mixing
6. Carbon offset purchases already made by employee

---

## Summary Table

| Source | Format | Real-world Shape | Key Challenge |
|--------|--------|-----------------|---------------|
| SAP | Flat CSV | German headers, plant codes | Unit inconsistency |
| Utility | Portal CSV | Non-calendar billing periods | PDF-only clients |
| Travel | JSON export | Mixed types, no distances | OAuth + pagination |