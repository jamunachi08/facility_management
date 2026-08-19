frappe.provide('frappe.dashboards.chart_sources');


frappe.dashboards.chart_sources['Rental Billing'] = {
    method: 'neotec_estate.neotec_estate.dashboard_chart_source.rental_billing.rental_billing.get'
}
