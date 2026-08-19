# -*- coding: utf-8 -*-
# Copyright (c) 2026, ERPNext Community and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FacilityCustodyLog(Document):

	def validate(self):
		if self.returned and not self.return_datetime:
			self.return_datetime = frappe.utils.now_datetime()
		self.update_set_status()

	def update_set_status(self):
		status = "In" if self.returned else "Out"
		frappe.db.set_value(self.reference_doctype, self.reference_set, "status", status)

