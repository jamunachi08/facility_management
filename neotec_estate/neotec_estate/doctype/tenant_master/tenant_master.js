// Copyright (c) 2020, 9T9IT and contributors
// For license information, please see license.txt
{% include 'neotec_estate/neotec_estate/doctype/tenant_master/js_controllers/index.js' %}

frappe.ui.form.on('Tenant Master', {
	refresh: refresh,
	first_name: first_name,
	last_name: last_name,
	tenant_type: tenant_type,
});
