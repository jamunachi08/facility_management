async function get_items(property_name) {
    const { message: items } = await frappe.call({
        method: 'neotec_estate.api.property_checkup.get_items',
        args: { property_name },
    });
    return items;
}
