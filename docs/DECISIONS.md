# DECISIONS.md — Design Decisions & Tradeoffs

## Every ambiguity I resolved, what I chose, and why.

---

## 1. SAP Export Format

**Question:** IDoc, flat file, OData, or BAPI?

**Decision:** Flat file CSV

**Why:**
SAP flat file exports are the most common format seen in 
real enterprise deployments. IDoc requires middleware (SAP PI/PO).
OData requires API access credentials. Flat file CSV is what 
a sustainability team actually receives via email or SFTP.

**What I ignored:**
- German column headers (handled by accepting any header)
- Plant code lookup tables (stored as-is in raw_data)
- Date format inconsistencies (stored as string, parse on normalize)

**What I'd ask the PM:**
Do clients have SAP API access or do they export manually?
What encoding do their exports use?

---

## 2. Utility Data Format

**Question:** Portal CSV, PDF bill, or API?

**Decision:** Portal CSV export

**Why:**
PDF parsing requires OCR which adds significant complexity.
Most utility portals (BSES, Adani, BESCOM) offer CSV export.
This is what a facilities team actually downloads monthly.

**What I ignored:**
- Tariff structure details (stored but not used in CO2 calc)
- Multi-meter aggregation
- Estimated vs actual readings

**What I'd ask the PM:**
Which utility providers do clients use?
Do they have portal access or only PDF bills?

---

## 3. Travel Data Format

**Question:** Concur API, Navan API, or CSV/JSON export?

**Decision:** JSON export (Concur-style)

**Why:**
Concur and Navan both offer JSON exports.
JSON handles mixed travel types (flight/hotel/ground)
better than CSV because each type has different fields.
CSV would require many empty columns.

**What I ignored:**
- Real Concur OAuth authentication
- Pagination for large datasets
- Carbon offsetting data

**What I'd ask the PM:**
Do clients use Concur or Navan?
Can we get API credentials or only manual exports?

---

## 4. Multi-tenancy Approach

**Decision:** Tenant FK on every model (data-level isolation)

**Why:**
Row-level multi-tenancy is simpler than schema-level or
database-level for a prototype. Every query filters by tenant.
Easy to audit and understand.

**Tradeoff:**
No middleware enforcement — a bug could theoretically
expose cross-tenant data. Acceptable for prototype.

---

## 5. Scope Assignment

**Decision:** Hardcoded by source type

**Why:**
- SAP fuel data → Scope 1 (direct combustion)
- Utility electricity → Scope 2 (indirect electricity)
- Corporate travel → Scope 3 (value chain)

This covers 80% of real cases. Edge cases (e.g. renewable
electricity = Scope 1) ignored for prototype.

**What I'd ask the PM:**
Do any clients have on-site renewable generation?
Do they need market-based vs location-based Scope 2?

---

## 6. Emission Factors

**Decision:** Hardcoded constants

**Why:**
A proper EmissionFactor table would require versioning,
source tracking (IPCC, GHG Protocol), and annual updates.
For a prototype, hardcoded factors from GHG Protocol are
sufficient and transparent.

**Factors used:**
- Diesel: 2.65 kgCO2e/liter (GHG Protocol)
- Petrol: 2.31 kgCO2e/liter (GHG Protocol)
- Natural Gas: 2.04 kgCO2e/m3 (GHG Protocol)
- Electricity: 0.91 kgCO2e/kWh (India CEA grid 2023)
- Flight economy: 0.16 kgCO2e/km (DEFRA 2023)
- Flight business: 0.43 kgCO2e/km (DEFRA 2023)
- Hotel: 31.0 kgCO2e/night (HCMI)
- Ground transport: 0.21 kgCO2e/km (DEFRA 2023)

---

## 7. Authentication

**Decision:** No auth for prototype

**Why:**
Adding JWT or session auth would double the complexity
without adding value to the core data pipeline demo.
The admin user is hardcoded for approve/reject actions.

**What I'd ask the PM:**
Will analysts log in via SSO or email/password?
Is role-based access (analyst vs auditor vs admin) required?

---

## 8. Duplicate Upload Prevention

**Decision:** Not implemented

**Why:**
Duplicate detection requires file hashing or unique
constraints on upload metadata. Out of scope for prototype.

**Real world fix:**
Hash the file on upload, reject if hash already exists
for that tenant.

---

## 9. Raw Data Storage

**Decision:** JSONField for raw_data in RawRecord

**Why:**
Every source has a different shape. A fixed schema would
require schema changes for every new source.
JSONField stores any shape without migration.
Trade-off: no SQL-level filtering on raw fields.

---

## 10. Deployment

**Decision:** Render.com (free tier)

**Why:**
Render supports Django + PostgreSQL + static files.
Free tier is sufficient for prototype demo.
Railway and Fly.io are alternatives but Render has
the simplest Django deployment flow.