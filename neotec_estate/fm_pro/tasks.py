# -*- coding: utf-8 -*-
# Copyright (c) 2026, ERPNext Community and contributors
# For license information, please see license.txt
"""
Scheduled jobs for the "Pro" feature set added on top of the original
Neotec Estate app: lease renewal reminders, maintenance SLA
escalation, rent-overdue notices and facility-booking cleanup.
Registered in hooks.py -> scheduler_events.
"""
import frappe
from frappe.utils import add_days, today, now_datetime, get_datetime, nowdate


def send_lease_renewal_reminders():
	"""Notify landlords/managers 30 days before a Rental Contract ends."""
	upcoming = add_days(today(), 30)
	contracts = frappe.get_all(
		"Rental Contract",
		filters={"contract_end_date": ["between", [today(), upcoming]], "docstatus": 1, "status": ["!=", "Cancelled"]},
		fields=["name", "tenant", "property", "contract_end_date"],
	)
	for c in contracts:
		try:
			_generate_notice(c.name, c.tenant, "Lease Renewal")
		except Exception:
			frappe.log_error(title=f"Lease renewal reminder failed: {c.name}", message=frappe.get_traceback())


def send_rent_overdue_notices():
	"""Notify tenants with an overdue Sales Invoice linked to a rental contract."""
	overdue_invoices = frappe.get_all(
		"Sales Invoice",
		filters={"outstanding_amount": [">", 0], "due_date": ["<", today()], "docstatus": 1},
		fields=["name", "customer", "outstanding_amount", "due_date"],
	)
	for inv in overdue_invoices:
		tenant = frappe.db.get_value("Tenant Master", {"customer": inv.customer}, "name")
		if not tenant:
			continue
		try:
			_generate_notice(None, tenant, "Rent Overdue", extra_context={"invoice": inv})
		except Exception:
			frappe.log_error(title=f"Rent overdue notice failed: {inv.name}", message=frappe.get_traceback())


def _generate_notice(rental_contract, tenant, notice_type, extra_context=None):
	template = frappe.db.get_value("Lease Template", {"is_default": 1}, "name")
	notice = frappe.get_doc(
		{
			"doctype": "Tenant Notice",
			"tenant": tenant,
			"rental_contract": rental_contract,
			"notice_type": notice_type,
			"lease_template": template,
		}
	)
	notice.insert(ignore_permissions=True)
	if template:
		notice.generate_and_send()


def escalate_overdue_maintenance():
	"""Email the assigned technician's manager for any Property Maintenance past `due_by`."""
	breached = frappe.get_all(
		"Property Maintenance",
		filters={"status": ["!=", "Closed"], "due_by": ["<", now_datetime()]},
		fields=["name", "assigned_to", "property", "ticket_priority"],
	)
	if not breached:
		return
	frappe.db.set_value(
		"Property Maintenance",
		{"name": ["in", [b.name for b in breached]]},
		"is_breached",
		1,
	)
	recipients = frappe.get_all("Has Role", filters={"role": "Facilities Manager"}, fields=["parent"])
	emails = [r.parent for r in recipients if "@" in (r.parent or "")]
	if not emails:
		return
	frappe.sendmail(
		recipients=emails,
		subject=frappe._("{0} maintenance ticket(s) have breached SLA").format(len(breached)),
		message=frappe.render_template(
			"<p>The following maintenance tickets are past their SLA due date:</p><ul>"
			"{% for row in tickets %}<li>{{ row.name }} - {{ row.property }} ({{ row.ticket_priority }})</li>{% endfor %}</ul>",
			{"tickets": breached},
		),
	)


def release_expired_facility_bookings():
	"""Auto-cancel Facility Bookings still 'Pending Approval' 24h after their start time."""
	stale = frappe.get_all(
		"Facility Booking",
		filters={"status": "Pending Approval", "from_datetime": ["<", add_days(now_datetime(), -1)]},
		fields=["name"],
	)
	for row in stale:
		frappe.db.set_value("Facility Booking", row.name, "status", "Cancelled")


def run_rental_increment_engine():
	"""
	Daily job: apply due Rental Increment Rules to their linked Rental
	Contract's rental_amount, then roll next_increment_date forward.
	Adapted from PropMS's property_increment engine, re-pointed at
	Rental Contract.rental_amount (the field Neotec Estate's own
	recurring-invoice engine already reads from) instead of PropMS's
	per-Lease-Item rate.
	"""
	due = frappe.get_all(
		"Rental Increment Rule",
		filters={"is_active": 1, "next_increment_date": ["<=", today()]},
		fields=["name"],
	)
	for row in due:
		rule = frappe.get_doc("Rental Increment Rule", row.name)
		try:
			new_amount = rule.apply_increment()
			frappe.logger("neotec_estate").info(
				f"Applied increment on {rule.rental_contract}: new rental_amount = {new_amount}"
			)
		except Exception:
			frappe.log_error(
				title=f"Rental increment failed: {rule.name}", message=frappe.get_traceback()
			)
