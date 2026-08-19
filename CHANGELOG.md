# Changelog — Neotec Estate

All notable changes to this app are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.1.0] — 2026-08-19

Feature port from **PropMS** (Aakvatech, MIT) — evaluated for direct
co-installation and rejected due to a hard `Property` doctype name
collision (Frappe doctype names are globally unique per site; PropMS
ships its own incompatible `Property` schema). Instead, the six
capability areas PropMS covers that Neotec Estate didn't were rebuilt as
native Neotec Estate doctypes, re-pointed at Neotec Estate's own
`Property` and `Rental Contract` instead of PropMS's, and consolidated
where PropMS had split near-duplicate doctypes (e.g. Guard vs Outsourcing
attendance) into one flexible model.

### Added
- **Utility metering** — `Meter` (linked to Property), `Meter Reading`
  (submittable; auto-computes consumption and amount from the previous
  reading, creates a Sales Invoice against the tenant's customer on
  submit unless `do_not_invoice` is set)
- **Rent increment automation** — `Rental Increment Rule` (percentage or
  fixed-amount, on a Months/Years cadence) with a daily scheduled job
  (`run_rental_increment_engine`) that bumps `Rental Contract.rental_amount`
  directly - the same field Neotec Estate's existing recurring-invoice
  engine already reads, so no other billing code needed to change
- **Security & workforce attendance** — `Facility Shift` (+ locations
  child table) and `Facility Attendance` (submittable), with a `category`
  field (Security/Outsourced/Other) covering what PropMS split across six
  separate doctypes (Guard Shift, Security Attendance, Outsourcing
  Category, Outsourcing Contact, Outsourcing Shift, Outsourcing
  Attendance)
- **Key & tool custody** — `Facility Key Set`, `Facility Tool Set`, and a
  shared `Facility Custody Log` (using a Dynamic Link to either set type)
  covering issue/return tracking that PropMS split across five doctypes
- **Daily inspection checklists** — `Checklist Area` (+ reusable task
  list) and `Property Daily Checklist` (submittable), with
  `populate_tasks_from_area()` to pre-fill an inspection round from a
  template area, and an optional link from a failed check straight to a
  `Property Maintenance` ticket
- **Maintenance material billing** — a `materials` child table
  (`Maintenance Material`) added to the existing `Property Maintenance`
  doctype (JSON-only change, controller untouched) plus a standalone
  `bill_materials()` function and a conditional "Bill Materials" button
  that creates a Sales Invoice for materials marked `Bill` or a Stock
  Entry for materials marked `Self Consumption`; requires a new
  `Default Maintenance Warehouse` field on Neotec Estate Settings for the
  self-consumption path
- Workspace: new "Ongoing operations" section (4 cards) alongside the
  existing 5-stage pathway

### Verified before release
- Doctype-name collision check against Neotec Estate, Neotec Optics, and
  documented ERPNext/HRMS core doctypes (zero collisions - `Facility
  Shift`/`Facility Attendance` are distinct strings from HRMS's `Shift
  Type`/`Shift Assignment`)
- Every `Table` field's `options` resolves to a real doctype in this app
- Every `Dynamic Link` field's `options` resolves to a real sibling field
- Every `fetch_from` reference resolves to a real sibling link field
- Class-name validator (`validate_classnames.py`) - zero mismatches
- Full JSON + `py_compile` pass across every file in the app

## [1.0.2] — 2026-08-19

### Added
- **Neotec Estate workspace** — a real Frappe v15 workspace (not the legacy
  `desktop.py` config carried over from the original app) with a 5-stage
  "pathway" of Card sections walking property setup → tenant onboarding →
  rent automation → maintenance & SLA → renewal & notices, plus shortcuts
  to FM Dashboard and Neotec Estate Settings. Structure verified against a
  real Frappe v15 core workspace file (`content`/`links`/`shortcuts`
  schema, `link_count` per card, block IDs) rather than guessed.

### Fixed
- **Critical: `ProgrammingError` opening FM Dashboard / calling
  `get_rental_listing`.** `neotec_estate/api/tenant_renting.py` and
  `fm_dashboard.py` still ran raw SQL against a `Tenant Renting` table
  and a `pm_tenant_renting` Sales Invoice field — both were removed from
  the *original* app years ago by patch
  `v0_4.remove_pm_tenant_renting` and replaced with `Rental Contract` /
  `pm_rental_contract`, but the query code was never updated to match.
  Every FM Dashboard page load and every call to `get_rental_listing`
  has been broken since that migration. Fixed both to query
  `Rental Contract` / `pm_rental_contract` correctly. (`fm_tenant`
  report was already correct and untouched.)

## [1.0.1] — 2026-08-19

### Fixed
- **Critical: `ImportError` opening Neotec Estate Settings.** The global
  rebrand from `facility_management` → `neotec_estate` matched
  `facility_management` (snake_case) and `Facility Management` (with a
  space), but missed the concatenated CamelCase class name
  `FacilityManagementSettings` in `neotec_estate_settings.py` — Frappe
  derives the controller class by stripping spaces/hyphens from the
  doctype name (`"Neotec Estate Settings" → NeotecEstateSettings`), so
  the module imported fine but the class lookup failed, surfacing as
  `ImportError: Neotec Estate Settings` on every attempt to open the
  Settings form.
  Fixed: class renamed to `NeotecEstateSettings` (and the matching test
  class to `TestNeotecEstateSettings`).
- **`Maintenance SLA` doctype had the same class-name bug**, introduced by
  the doctype generator itself (title-casing `"sla"` → `"Sla"` instead of
  preserving the acronym). Class renamed from `MaintenanceSla` to
  `MaintenanceSLA` to match the doctype name exactly.
- Added `validate_classnames.py` as a build-time check (not shipped in
  the app) that compares every doctype's JSON `name` against its
  controller's actual class name, to catch this class of bug before
  release going forward.

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
