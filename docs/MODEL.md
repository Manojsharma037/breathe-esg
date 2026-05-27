# Data Model — BreatheESG Ingestion Platform

## Why This Model?

The core challenge is not computing carbon — it's that every client's 
data arrives in a different shape. This model separates raw ingestion 
from normalized records deliberately.

---

## Models

### Tenant
Represents a client company. Every piece of data is scoped to a tenant.
Multi-tenancy is handled at the data level, not middleware level — 
simple and auditable.

### UserProfile
Extends Django's built-in User to attach a tenant. An analyst belongs 
to exactly one tenant and can only see that tenant's data.

### DataUpload
Tracks every file ingestion event. Source type (SAP/utility/travel), 
who uploaded it, when, and whether processing succeeded or failed.
This is the entry point for all data.

### RawRecord
Stores every row exactly as it came in — no transformation. 
raw_data is a JSONField so any source shape fits.
This is the source of truth. If something goes wrong in normalization,
we can always re-process from here.

### NormalizedRecord
The processed version of a RawRecord. Units converted to kg,
scope assigned, CO2e calculated. This is what analysts review.

Key fields:
- scope: Scope 1 / 2 / 3
- original_unit → normalized_quantity (always in kg)
- co2_equivalent (kgCO2e)
- review_status: pending → approved/rejected
- is_suspicious: flagged for analyst attention
- is_locked: locked after audit, cannot be edited

### AuditLog
Every action tracked — upload, approve, reject, edit, lock.
Who did what and when. Required for audit trail.

---

## Relationships

Tenant → DataUpload → RawRecord → NormalizedRecord → AuditLog

---

## Key Design Decisions

1. Raw and normalized are separate tables — raw data is never modified
2. JSONField for raw_data — handles any source shape without schema changes
3. Tenant FK on every model — clean multi-tenancy
4. is_locked flag — prevents edits after audit sign-off
5. period_start/end on NormalizedRecord — billing periods dont align 
   with calendar months (utility data reality)

---

## Tradeoffs

- No separate EmissionFactor table — hardcoded factors for now
- No row-level permissions — tenant isolation is sufficient for prototype
- SQLite in dev, PostgreSQL in production