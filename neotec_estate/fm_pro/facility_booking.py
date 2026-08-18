# -*- coding: utf-8 -*-
# Copyright (c) 2026, ERPNext Community and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.utils import flt, time_diff_in_hours, get_datetime


def validate_booking(doc, method=None):
	if not doc.facility_asset:
		return
	if get_datetime(doc.from_datetime) >= get_datetime(doc.to_datetime):
		frappe.throw(_("'From' must be before 'To'"))

	_check_overlap(doc)
	_set_amount(doc)

	requires_approval = frappe.db.get_value("Facility Asset", doc.facility_asset, "requires_approval")
	if requires_approval and doc.status == "Confirmed" and doc.is_new():
		doc.status = "Pending Approval"


def _check_overlap(doc):
	clash = frappe.db.sql(
		"""
		SELECT name FROM `tabFacility Booking`
		WHERE facility_asset = %(facility_asset)s
		AND name != %(name)s
		AND status not in ('Cancelled')
		AND (from_datetime < %(to)s AND to_datetime > %(from)s)
		""",
		{
			"facility_asset": doc.facility_asset,
			"name": doc.name or "New Facility Booking",
			"from": doc.from_datetime,
			"to": doc.to_datetime,
		},
	)
	if clash:
		frappe.throw(
			_("{0} is already booked for an overlapping time slot ({1}).").format(
				doc.facility_asset, clash[0][0]
			)
		)


def _set_amount(doc):
	rate = frappe.db.get_value("Facility Asset", doc.facility_asset, "hourly_rate") or 0
	hours = time_diff_in_hours(doc.to_datetime, doc.from_datetime)
	doc.total_amount = flt(rate) * flt(hours)


def on_submit_booking(doc, method=None):
	doc.status = doc.status if doc.status != "Pending Approval" else "Pending Approval"
