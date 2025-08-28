# Copyright 2025 Loym
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Assign Partner Location",
    "summary": "",
    "author": "FIQ, Loym",
    "data": [
        "security/ir.model.access.csv",
        "views/crm_lead_views.xml",
        "views/res_partner_assign_location_views.xml",
        "views/res_partner_views.xml",
    ],
    "depends": [
        "base_location",
        "contacts",
        "crm", # Move to separate module
    ],
    "license": "AGPL-3",
    "version": "18.0.1.0.1",
    # "website": "https://www.loym.com",
}
