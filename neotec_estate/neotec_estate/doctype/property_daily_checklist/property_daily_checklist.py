# -*- coding: utf-8 -*-
# Copyright (c) 2026, ERPNext Community and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PropertyDailyChecklist(Document):

	@frappe.whitelist()
	def populate_tasks_from_area(self):
		if not self.area:
			return
		area = frappe.get_doc("Checklist Area", self.area)
		self.set("details", [])
		for task in area.tasks:
			self.append("details", {"checklist_task": task.task_name, "status": "OK"})

