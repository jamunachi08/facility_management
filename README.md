# Neotec Estate

**Version 1.1.0** · ERPNext v15 / Frappe Framework v15 · [Changelog](CHANGELOG.md)

**Facility & Real Estate Management — for ERPNext v15 / Frappe Framework v15**

An app that unifies two disciplines that almost always live under the same
operator in the real world — building **Facility Management (CMMS)** and
**Real Estate / Property Management** — into a single installable app,
under the Neotec brand.

This is a v15-compatible evolution of the original `facility_management`
app (originally by 9T9IT, MIT licensed), which already modeled Property,
Landlord, Tenant and Rental Contract side-by-side with Property
Maintenance — confirming a merge is the natural shape of this domain, not
a forced combination.

## Why merged, not split

Facility managers and property managers are usually the same team with the
same building, the same tenants, and the same maintenance vendors. Splitting
them into two apps would mean duplicating Property, Tenant and Vendor
master data across two systems. One app, two workspaces.

## What's new in Neotec Estate (v1.0.0)

Added on top of the original doctype set, drawing on patterns from
**MicroRealEstate** (open-source rental SaaS), **NUcore** (enterprise core-
facility equipment booking & billing), and industry leaders (Yardi,
Buildium, AppFolio, UpKeep, Fiix):

| Feature | Doctype(s) | Inspired by |
|---|---|---|
| **Bookable facility assets** — meeting rooms, halls, gym equipment, parking slots, with hourly/daily rates and approval workflow | `Facility Asset`, `Facility Booking` | NUcore's instrument/equipment reservation & price-policy model |
| **Maintenance SLAs** — response/resolution targets per priority, auto due-date calc, breach flag, escalation email | `Maintenance SLA` (+2 new fields on `Property Maintenance`) | Standard CMMS practice (UpKeep, Fiix) |
| **Lease & notice document generation** — Jinja-templated contracts, rent-overdue notices, renewal reminders, rendered and emailed automatically | `Lease Template`, `Tenant Notice` | MicroRealEstate's custom document/mass-notice engine |
| **Automated lifecycle jobs** — 30-day lease renewal reminders, rent-overdue notices, SLA breach escalation, stale-booking cleanup | `fm_pro/tasks.py` (scheduler) | MicroRealEstate's rent tracking + notices |
| **Tenant self-service portal** | portal menu: My Lease, Maintenance Requests, Book a Facility | MicroRealEstate's tenant portal |
| **New roles** | `Facilities Manager`, `Tenant` | — |

The original modules are untouched and fully intact: `Property`,
`Real Estate Property`, `Landlord`, `Tenant Master`, `Rental Contract`,
`Property Maintenance`, `Property Checkup`, `Property Inventory`,
`EWA Billing`, `Tenant Violation`, `Neotec Estate Settings`, automatic
recurring rent invoicing, and the FM Dashboard reports.

## What's new in v1.1.0 — ported from PropMS

Evaluated **PropMS** (Aakvatech, MIT-licensed) for direct
co-installation and found a hard blocker: it ships its own `Property`
doctype with an incompatible schema, and Frappe doctype names are
globally unique per site, so installing both apps on the same site would
collide on the single most central doctype in either. Instead, the six
capability areas PropMS covers that Neotec Estate didn't were rebuilt as
native doctypes here, pointed at *this* app's `Property` and
`Rental Contract`:

| Feature | Doctype(s) | Consolidated from PropMS |
|---|---|---|
| Utility metering & auto-billing | `Meter`, `Meter Reading` | 1:1, re-pointed at our `Property` |
| Rent increment automation | `Rental Increment Rule` | 1:1, targets `Rental Contract.rental_amount` directly |
| Security & workforce attendance | `Facility Shift`, `Facility Attendance` | 6 PropMS doctypes (Guard/Outsourcing split) → 2, via a `category` field |
| Key & tool custody | `Facility Key Set`, `Facility Tool Set`, `Facility Custody Log` | 5 PropMS doctypes → 3, via a shared Dynamic-Link custody log |
| Daily inspection checklists | `Checklist Area`, `Property Daily Checklist` | 1:1, with an escalation link into `Property Maintenance` |
| Maintenance material billing | `Maintenance Material` (added to `Property Maintenance`) | 2 PropMS doctypes → 1 child table, plus a `bill_materials()` action |

Total doctypes in this app: 41.

## Installation (ERPNext v15)

```bash
bench get-app neotec_estate /path/to/neotec_estate
bench --site your-site.local install-app neotec_estate
bench --site your-site.local migrate
```

Requires `frappe` and `erpnext` v15 (declared via `required_apps` in
`hooks.py` and `pyproject.toml`).

## Roadmap (not yet built — natural next increments)

- E-signature integration for `Lease Template` output (DocuSign/local e-sign)
- Owner/landlord statement of accounts + disbursement runs (Yardi/Buildium-style)
- Move-in/move-out condition inspection checklist tied to `Property Checkup`
- Vendor SLA scorecards for `Asset Repair` / contractor performance
- Multi-currency deposit escrow tracking
- Mobile-first tenant portal (Frappe UI / PWA) for the "My Lease" and
  "Maintenance Requests" pages

## License

MIT
