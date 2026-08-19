# Changelog — Neotec Estate

All notable changes to this app are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] — 2026-08-19

Initial Neotec release. Rebuilt for **ERPNext v15 / Frappe Framework v15**
on top of the original `facility_management` app (9T9IT, MIT), with a new
"Pro" feature layer added on top.

### Added — new in this release
- **Facility Asset** — bookable rooms, halls, equipment, amenities, parking
  slots; hourly/daily rates; approval flag
- **Facility Booking** — reservation doctype with automatic overlap
  prevention, auto-computed total from asset rate × duration, optional
  approval workflow
- **Maintenance SLA** — response/resolution time targets per priority
- Two new fields on `Property Maintenance`: `due_by` (auto-calculated from
  SLA) and `is_breached` (auto-flagged), wired via a `validate` doc_event
  so the original doctype needed no rewrite
- **Lease Template** — Jinja-templated document definitions for contracts
  and notices, with merge fields for tenant/property/contract data
- **Tenant Notice** — generates and sends (email/SMS/both) a rendered
  notice from a Lease Template; `generate_and_send()` whitelisted method
- Scheduled jobs: 30-day lease renewal reminders, rent-overdue notices,
  maintenance SLA breach escalation email, stale-booking auto-cancel
- Tenant self-service portal menu: My Lease, Maintenance Requests, Book a
  Facility
- New roles: `Facilities Manager`, `Tenant`, with permissions wired into
  every original doctype (Property, Rental Contract, Property Maintenance,
  Tenant Master, Landlord, Property Checkup)
- v15 packaging: `pyproject.toml` with `[tool.bench.frappe-dependencies]`
  (`frappe`/`erpnext` `>=15.0.0,<16.0.0`), `hooks.py` `required_apps`

### Changed
- App renamed end-to-end: `facility_management` → `neotec_estate`
  (package, module, `modules.txt`, every doctype's `module` field, config
  file). `Facility Management Settings` → `Neotec Estate Settings`.
- `app_title` → "Neotec Estate", `app_publisher` → "Neotec"
- `ticket_priority` on Property Maintenance widened: added "Urgent"

### Unchanged (carried over from the original app)
`Property`, `Real Estate Property`, `Landlord`, `Tenant Master`,
`Rental Contract`, `Property Maintenance`, `Property Checkup`,
`Property Inventory`, `EWA Billing`, `Tenant Violation`, automatic
recurring rent invoicing, FM Dashboard reports.

### Roadmap (not in this release)
See README.md — e-signature integration, owner disbursement runs,
move-in/move-out inspection checklist, contractor SLA scorecards,
multi-currency escrow, mobile-first portal.
