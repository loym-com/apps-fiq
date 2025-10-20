# Copyright 2025 Loym
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "CRM: Create sale order and project",
    "summary": "",
    "author": "Loym, FIQ",
    "data": [
    ],
    "depends": [
        "base_display_name", # sale.order.name: _get_value_from_indexed_pattern()
        # "crm_security_group",
        "partner_short_name",
        "portal_user", # dummy placeholders
        "sale_crm",
        "sale_project",
    ],
    "license": "AGPL-3",
    "version": "18.0.5.0.1",
    "website": "https://www.loym.com",
}
