# -*- coding: utf-8 -*-
# Copyright (c) 2026, ERPNext Community and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RentalIncrementRule(Document):

	def validate(self):
		if not self.next_increment_date:
			self.next_increment_date = self.effective_from

	def apply_increment(self):
		"""Bump the linked Rental Contract's rental_amount and roll the next due date forward."""
		from frappe.utils import add_months, flt, getdate, today

		contract = frappe.get_doc("Rental Contract", self.rental_contract)
		current = flt(contract.rental_amount)
		if self.increment_type == "Percentage":
			new_amount = current + (current * flt(self.increment_value) / 100)
		else:
			new_amount = current + flt(self.increment_value)

		contract.db_set("rental_amount", new_amount)

		months = self.increment_every if self.increment_uom == "Months" else self.increment_every * 12
		self.last_applied_on = today()
		self.next_increment_date = add_months(getdate(self.next_increment_date), months)
		self.db_update()
		return new_amount

