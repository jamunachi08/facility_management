# -*- coding: utf-8 -*-
# Copyright (c) 2026, ERPNext Community and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TenantNotice(Document):

	def before_insert(self):
		if self.lease_template and not self.rendered_content:
			self.render_from_template()

	def render_from_template(self):
		template = frappe.get_doc("Lease Template", self.lease_template)
		context = self.get_merge_context()
		self.subject = frappe.render_template(template.subject or template.template_name, context)
		self.rendered_content = frappe.render_template(template.content, context)

	def get_merge_context(self):
		context = {"tenant": frappe.get_doc("Tenant Master", self.tenant)}
		if self.rental_contract:
			context["rental_contract"] = frappe.get_doc("Rental Contract", self.rental_contract)
			context["property"] = frappe.get_doc("Property", context["rental_contract"].property)
		return context

	@frappe.whitelist()
	def generate_and_send(self):
		if not self.rendered_content and self.lease_template:
			self.render_from_template()
			self.save(ignore_permissions=True)

		email = frappe.db.get_value("Tenant Master", self.tenant, "email")
		if self.sent_via in ("Email", "Both") and email:
			frappe.sendmail(
				recipients=[email],
				subject=self.subject or self.notice_type,
				message=self.rendered_content or self.notice_type,
			)
		if self.sent_via in ("SMS", "Both"):
			mobile = frappe.db.get_value("Tenant Master", self.tenant, "mobile_no")
			if mobile:
				from frappe.core.doctype.sms_settings.sms_settings import send_sms

				send_sms([mobile], frappe.utils.strip_html(self.rendered_content or self.notice_type)[:300])

		self.sent = 1
		self.sent_on = frappe.utils.now_datetime()
		self.db_update()
		return True

