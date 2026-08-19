# -*- coding: utf-8 -*-
# Copyright (c) 2026, ERPNext Community and contributors
# For license information, please see license.txt
"""
Wires "Maintenance SLA" (response/resolution targets per priority) into the
existing Property Maintenance doctype via a doc_events "validate" hook, so
the core doctype JSON only needed two new read-only fields (due_by,
resolved_on, is_breached) instead of a full rewrite.
"""
import frappe
from frappe.utils import add_to_date, get_datetime, now_datetime


def set_sla_dates(doc, method=None):
	"""Called on Property Maintenance.validate"""
	if not doc.raised_on:
		doc.raised_on = now_datetime()

	sla = _get_sla(doc.ticket_priority)
	if sla and not doc.due_by:
		doc.due_by = add_to_date(get_datetime(doc.raised_on), hours=sla.resolution_time_hours)

	if doc.status == "Closed" and not doc.resolved_on:
		doc.resolved_on = now_datetime()

	if doc.due_by:
		reference = get_datetime(doc.resolved_on) if doc.resolved_on else now_datetime()
		doc.is_breached = 1 if reference > get_datetime(doc.due_by) else 0


def _get_sla(priority):
	if not priority:
		return None
	name = frappe.db.get_value(
		"Maintenance SLA", {"priority": priority}, ["response_time_hours", "resolution_time_hours"], as_dict=True
	)
	return name
