# Neotec Estate

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
