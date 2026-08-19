# -*- coding: utf-8 -*-
# Copyright (c) 2026, ERPNext Community and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class MeterReading(Document):

	def validate(self):
		self.set_previous_reading()
		self.calculate_consumption_and_amount()

	def set_previous_reading(self):
		if self.previous_reading:
			return
		last = frappe.get_all(
			"Meter Reading",
			filters={"meter": self.meter, "docstatus": 1, "name": ["!=", self.name]},
			fields=["current_reading"],
			order_by="reading_date desc",
			limit=1,
		)
		if last:
			self.previous_reading = last[0].current_reading
		else:
			self.previous_reading = frappe.db.get_value("Meter", self.meter, "initial_reading") or 0

	def calculate_consumption_and_amount(self):
		self.consumption = flt(self.current_reading) - flt(self.previous_reading)
		if self.consumption < 0:
			frappe.throw(frappe._("Current reading cannot be less than the previous reading ({0})").format(self.previous_reading))

		if not self.rate:
			meter_type = frappe.db.get_value("Meter", self.meter, "meter_type")
			self.rate = frappe.db.get_value("Item Price", {"item_code": meter_type, "selling": 1}, "price_list_rate") or 0

		self.amount = flt(self.consumption) * flt(self.rate)

	def on_submit(self):
		if not self.do_not_invoice:
			self.create_utility_invoice()

	def create_utility_invoice(self):
		meter = frappe.get_doc("Meter", self.meter)
		customer = meter.invoice_customer
		if not customer:
			rental_contract = frappe.db.get_value(
				"Rental Contract", {"property": meter.property, "status": "Active"}, "tenant"
			)
			if rental_contract:
				customer = frappe.db.get_value("Tenant Master", rental_contract, "customer")
		if not customer:
			frappe.msgprint(frappe._("No invoice customer found for meter {0}; invoice not created.").format(self.meter))
			return

		invoice = frappe.new_doc("Sales Invoice")
		invoice.customer = customer
		invoice.append("items", {
			"item_code": meter.meter_type,
			"qty": self.consumption,
			"rate": self.rate,
		})
		invoice.set_missing_values()
		invoice.insert(ignore_permissions=True)
		self.db_set("sales_invoice", invoice.name)

