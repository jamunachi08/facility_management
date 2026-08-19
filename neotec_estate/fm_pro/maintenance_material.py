# -*- coding: utf-8 -*-
# Copyright (c) 2026, ERPNext Community and contributors
# For license information, please see license.txt
"""
Bills or consumes materials logged against a Property Maintenance ticket.
Adapted from PropMS (Aakvatech)'s Issue Materials Billed/Detail pattern,
re-pointed at Neotec Estate's Property Maintenance instead of ERPNext's
core Issue doctype, and consolidated into a single child table
(`Maintenance Material`) with a `material_status` field driving whether a
row is billed to the tenant (Sales Invoice) or consumed internally
(Stock Entry) rather than two separate child doctypes.

Kept as a standalone whitelisted function (not a Document method) so the
original, unmodified `PropertyMaintenance` controller class never needed
to be touched - only its JSON gained a `materials` table field via a
doc_events-free JSON patch, matching how the SLA fields were added.
"""
import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def bill_materials(property_maintenance):
	doc = frappe.get_doc("Property Maintenance", property_maintenance)

	to_bill = [
		row for row in doc.materials
		if row.material_status == "Bill" and not row.invoiced
	]
	to_consume = [
		row for row in doc.materials
		if row.material_status == "Self Consumption" and not row.invoiced
	]

	if not to_bill and not to_consume:
		frappe.msgprint(_("No unbilled materials found on this ticket."))
		return

	if to_bill:
		_create_sales_invoice(doc, to_bill)
	if to_consume:
		_create_stock_entry(doc, to_consume)


def _create_sales_invoice(doc, rows):
	customer = frappe.db.get_value("Tenant Master", doc.tenant, "customer") if doc.tenant else None
	if not customer:
		frappe.throw(_("Cannot bill materials: {0} has no linked Tenant with a Customer.").format(doc.name))

	invoice = frappe.new_doc("Sales Invoice")
	invoice.customer = customer
	for row in rows:
		invoice.append("items", {
			"item_code": row.item,
			"qty": flt(row.quantity),
			"rate": flt(row.rate),
			"uom": row.uom,
		})
	invoice.set_missing_values()
	invoice.insert(ignore_permissions=True)

	for row in rows:
		row.db_set("invoiced", 1)
		row.db_set("sales_invoice", invoice.name)


def _create_stock_entry(doc, rows):
	default_warehouse = frappe.db.get_single_value("Neotec Estate Settings", "default_maintenance_warehouse")
	if not default_warehouse:
		frappe.throw(
			_("Set a Default Maintenance Warehouse in Neotec Estate Settings before recording self-consumption.")
		)

	entry = frappe.new_doc("Stock Entry")
	entry.stock_entry_type = "Material Issue"
	for row in rows:
		entry.append("items", {
			"item_code": row.item,
			"qty": flt(row.quantity),
			"s_warehouse": default_warehouse,
			"uom": row.uom,
		})
	entry.insert(ignore_permissions=True)

	for row in rows:
		row.db_set("invoiced", 1)
		row.db_set("stock_entry", entry.name)
