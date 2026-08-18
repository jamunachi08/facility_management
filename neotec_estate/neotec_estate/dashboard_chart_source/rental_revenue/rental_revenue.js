frappe.provide('frappe.dashboards.chart_sources');


frappe.dashboards.chart_sources['Rental Revenue'] = {
    method: 'neotec_estate.neotec_estate.dashboard_chart_source.rental_revenue.rental_revenue.get'
}
