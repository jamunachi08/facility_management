frappe.provide('frappe.dashboards.chart_sources');


frappe.dashboards.chart_sources['Rental Value'] = {
    method: 'neotec_estate.neotec_estate.dashboard_chart_source.rental_value.rental_value.get'
}
