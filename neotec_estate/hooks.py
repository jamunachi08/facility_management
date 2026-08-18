# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "neotec_estate"
app_title = "Neotec Estate"
app_publisher = "Neotec"
app_description = (
    "ERPNext v15 app that unifies Facility Management (CMMS, bookable assets, "
    "maintenance SLAs) with Real Estate Management (landlords, tenants, leases, "
    "rent automation, tenant self-service portal) under the Neotec brand."
)
app_icon = "octicon octicon-home"
app_color = "green"
app_email = "info@neotec.app"
app_license = "MIT"

# v15: declare hard dependency so `bench get-app` / CI installs erpnext first
required_apps = ["frappe", "erpnext"]

fixtures = [
    "Role",
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "Expense Claim-pm_property_maintenance",
                    "Material Request-pm_property_maintenance",
                    "Asset Repair-pm_property_maintenance",
                    "Sales Invoice-pm_rental_contract",
                    "Sales Invoice-pm_property_sb",
                    "Sales Invoice-pm_property",
                    "Sales Invoice-pm_tenant",
                    "Sales Invoice-pm_property_group"
                ]
            ]
        ]
    },
    {
        "doctype": "Property Setter",
        "filters": [
            [
                "name",
                "in",
                [
                    "Dashboard Chart-type-options"
                ]
            ]
        ]
    },
    {
        "doctype": "Dashboard Chart",
        "filters": [
            [
                "name",
                "in",
                [
                    "Rental Value",
                    "Rental Revenue",
                    "Rental Billing",
                    "Rental Property Occupancy"
                ]
            ]
        ]
    }
]
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/neotec_estate/css/neotec_estate.css"
# app_include_js = "/assets/neotec_estate/js/neotec_estate.js"

# include js, css files in header of web template
# web_include_css = "/assets/neotec_estate/css/neotec_estate.css"
# web_include_js = "/assets/neotec_estate/js/neotec_estate.js"

# include js in page
page_js = {"dashboard": "public/js/dashboard.js"}

# include js in doctype views
doctype_js = {
    "Sales Invoice": "public/js/scripts/sales_invoice.js",
    "Payment Entry": "public/js/scripts/payment_entry.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "neotec_estate.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "neotec_estate.install.before_install"
# after_install = "neotec_estate.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "neotec_estate.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Invoice": {
        "validate": "neotec_estate.doc_events.sales_invoice.validate",
    },
    "Property Maintenance": {
        "validate": "neotec_estate.fm_pro.maintenance_sla.set_sla_dates",
    },
    "Facility Booking": {
        "validate": "neotec_estate.fm_pro.facility_booking.validate_booking",
        "on_submit": "neotec_estate.fm_pro.facility_booking.on_submit_booking",
    },
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": [
        "neotec_estate.events.create_invoice.execute",
        "neotec_estate.events.cancel_rental_contract.execute",
        # -- new in Facility & Real Estate Management Pro --
        "neotec_estate.fm_pro.tasks.send_lease_renewal_reminders",
        "neotec_estate.fm_pro.tasks.escalate_overdue_maintenance",
        "neotec_estate.fm_pro.tasks.send_rent_overdue_notices",
    ],
    "hourly": [
        "neotec_estate.fm_pro.tasks.release_expired_facility_bookings",
    ],
}

# Standard Portal Menu Items (tenant self-service)
# -------------------------------------------------
standard_portal_menu_items = [
    {"title": "My Lease", "route": "/my-lease", "reference_doctype": "Rental Contract"},
    {"title": "Maintenance Requests", "route": "/maintenance-requests", "reference_doctype": "Property Maintenance"},
    {"title": "Book a Facility", "route": "/facility-bookings", "reference_doctype": "Facility Booking"},
]

# Testing
# -------

# before_tests = "neotec_estate.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "neotec_estate.event.get_events"
# }

jenv = {
    "methods": [
        "get_landlord_details:neotec_estate.api.tenant_renting.get_landlord_details",
        "get_tenant_details:neotec_estate.api.tenant_renting.get_tenant_details"
    ]
}
