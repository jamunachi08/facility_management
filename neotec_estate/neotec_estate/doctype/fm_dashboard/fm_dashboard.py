# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class FMDashboard(Document):
	def make_outstanding_balances(self):
		"""
		Make outstanding balances for display
		:return:
		"""
		self.outstanding_balances = None

		outstanding_balances = _get_outstanding_balances(_get_properties(self.real_estate_property))
		for outstanding_balance in outstanding_balances:
			self.append('outstanding_balances', {
				'property_name': outstanding_balance.get('property_name'),
				'sales_invoice': outstanding_balance.get('sales_invoice'),
				'outstanding_amount': outstanding_balance.get('outstanding_amount')
			})


def _get_properties(real_estate_property):
	return list(map(lambda x: x['name'], frappe.get_all('Property', {'property_location': real_estate_property})))


def _get_outstanding_balances(filter_properties):
	"""
	Historical note: this previously joined Sales Invoice to a
	`Tenant Renting` table via a `pm_tenant_renting` field on Sales
	Invoice. Both were removed in patch v0_4
	(facility_management.patches.v0_4.remove_pm_tenant_renting) and
	replaced by `Rental Contract` / the `pm_rental_contract` field on
	Sales Invoice, but this function was never updated to match - it kept
	referencing the dropped table and field, which threw a SQL error on
	every FM Dashboard page load. Fixed here to join through
	`Rental Contract` instead.
	"""
	def make_data(balance):
		property_name = _get_property_name(balance.get('pm_rental_contract'))
		return {
			'property_name': property_name,
			'sales_invoice': balance.get('name'),
			'outstanding_amount': balance.get('outstanding_amount')
		}

	outstanding = frappe.db.sql("""
		SELECT
			si.name,
			si.pm_rental_contract,
			si.outstanding_amount,
			rc.property
		FROM `tabSales Invoice` si
		LEFT JOIN `tabRental Contract` rc ON si.pm_rental_contract = rc.name
		WHERE si.docstatus = 1
		AND si.outstanding_amount > 0
		AND si.pm_rental_contract IS NOT NULL
		AND si.pm_rental_contract != ''
	""", as_dict=True)

	outstanding = filter(lambda x: x['property'] in filter_properties, outstanding)

	return list(map(make_data, outstanding))


def _get_property_name(rental_contract):
	if not rental_contract:
		return None
	data = frappe.db.sql("""
		SELECT p.title
		FROM `tabRental Contract` rc
		JOIN `tabProperty` p
		ON rc.property = p.name
		WHERE rc.name = %s
	""", rental_contract, as_dict=True)
	return data[0]['title'] if data else None
