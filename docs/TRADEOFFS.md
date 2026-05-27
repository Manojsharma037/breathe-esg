# TRADEOFFS.md — What I Deliberately Did Not Build

## Three things I chose not to build, and why.

---

## 1. Authentication & Role-Based Access Control

**What I didn't build:**
- User login/logout
- JWT tokens
- Role-based permissions (analyst vs auditor vs admin)
- Per-tenant user isolation at middleware level

**Why I skipped it:**
The assignment asked for a prototype that demonstrates
the data pipeline — ingest, normalize, review, audit.
Adding auth would double the codebase complexity without
adding value to the core ESG data flow.

A real deployment would need:
- SSO integration (Google/Microsoft)
- Role-based access (analyst can approve, auditor can only view)
- Per-tenant data isolation enforced at middleware level
- Session management and token refresh

**What I'd do in production:**
Django's built-in auth + DRF TokenAuthentication or
django-allauth for SSO. Tenant middleware to enforce
data isolation at request level.

---

## 2. Emission Factor Management System

**What I didn't build:**
- EmissionFactor database table
- Factor versioning (factors change every year)
- Source tracking (IPCC vs DEFRA vs CEA)
- Country/region specific factors
- Market-based vs location-based Scope 2 factors

**Why I skipped it:**
A proper EmissionFactor table would require:
- Annual update workflow
- Audit trail for factor changes
- Retroactive recalculation when factors update
- Multiple factor sets per category

This is a product feature on its own.
Not a prototype concern.

**Current approach:**
Hardcoded constants in normalizer.py with clear
comments citing the source (GHG Protocol, DEFRA 2023, CEA).
Transparent and defensible for a prototype.

**What I'd do in production:**
EmissionFactor model with fields:
- category
- factor_value
- unit
- source (GHG Protocol / DEFRA / CEA)
- valid_from / valid_to
- country/region

Normalization would look up the active factor
at time of data ingestion.

---

## 3. Real-time Data Pipeline & Scheduling

**What I didn't build:**
- Scheduled automatic ingestion (cron jobs)
- API pull from SAP OData service
- Utility portal API integration
- Concur/Navan OAuth + API polling
- Celery task queue for async processing
- Real-time notifications when new data arrives

**Why I skipped it:**
The assignment said to pick one ingestion mechanism
and justify it. Scheduled pulls require:
- Celery + Redis for task queue
- Credential management for each client
- Error handling for API downtime
- Retry logic for failed ingestions

This is infrastructure complexity that would obscure
the core data model and normalization logic.

**Current approach:**
Manual file upload via UI. An analyst uploads the
export they received. This is realistic for many
mid-size enterprise clients who don't have API
access to their own systems.

**What I'd do in production:**
- Celery Beat for scheduled pulls
- Encrypted credential storage per tenant
- Webhook receivers for push-based sources
- Dead letter queue for failed ingestions

---

## Summary

| Feature | Decision | Reason |
|---------|----------|--------|
| Authentication | Skipped | Core pipeline more important |
| EmissionFactor table | Skipped | Hardcoded factors sufficient |
| Scheduled ingestion | Skipped | Manual upload realistic enough |