from functools import reduce

import frappe
from frappe.utils.data import nowdate


@frappe.whitelist()
def get_rental_listing():
    def data_occupied(rental):
        name = rental.get("name")
        return {"occupied": name in rented_properties}

    rented_properties = _get_rented_properties()
    occupied = list(map(data_occupied, _get_rental_properties()))

    return {
        "Vacant": len(list(filter(lambda x: not x["occupied"], occupied))),
        "Occupied": len(list(filter(lambda x: x["occupied"], occupied))),
    }


@frappe.whitelist()
def get_customer(tenant_renting):
    """
    Deprecated
    :param tenant_renting:
    :return:
    """
    tenant = frappe.db.get_value("Rental Contract", tenant_renting, "tenant")
    return frappe.db.get_value("Tenant Master", tenant, "customer")


def get_landlord_details(property):
    landlord = frappe.db.get_value("Property", property, "landlord")
    cpr = frappe.db.get_value("Landlord", landlord, "cpr")
    return {"name": landlord, "cpr": cpr}


def get_tenant_details(tenant):
    tenant_details = frappe.db.sql(
        """
            SELECT tenant_name, cpr, passport_no
            FROM `tabTenant Master`
            WHERE name = %(tenant)s
        """,
        {"tenant": tenant},
        as_dict=1,
    )
    return tenant_details[0] if tenant_details else None


def _get_rental_properties():
    return frappe.db.sql(
        """
            SELECT
                p.name,
                p.title,
                p.property_type
            FROM `tabProperty` p
            WHERE p.property_status = 'Rental'
        """,
        as_dict=True,
    )


def _get_rented_properties():
    """
    A Rental Contract is 'active occupancy' for vacant/occupied purposes
    when today falls within its start/end dates and it hasn't been
    cancelled. `docstatus = 1` (submitted) additionally excludes drafts
    from counting as an actual rental.

    Historical note: this previously queried a `Tenant Renting` table
    that was removed in patch v0_4 (see
    facility_management.patches.v0_4.remove_pm_tenant_renting) and
    replaced by `Rental Contract`, but this function itself was never
    updated to match - it kept querying the dropped table directly via
    raw SQL, which threw a "table doesn't exist" error on every call.
    Fixed here to query `Rental Contract` instead.
    """

    def make_data(rental_contract):
        return rental_contract.get("property")

    return list(
        map(
            make_data,
            frappe.db.sql(
                """
                    SELECT property
                    FROM `tabRental Contract`
                    WHERE docstatus = 1
                    AND status != 'Cancelled'
                    AND %s BETWEEN contract_start_date AND contract_end_date
                """,
                nowdate(),
                as_dict=True,
            ),
        )
    )
