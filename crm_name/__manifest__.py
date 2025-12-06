# Copyright 2025 FIQ & Loym
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


{
    "name": "CRM Name",
    "summary": "",
    "author": "FIQ, Loym",
    "data": [
        "views/crm_lead_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "depends": [
        "base_mixin_expression_value",
        "crm",
        "partner_short_name",
    ],
    "license": "AGPL-3",
    "post_init_hook": "post_init_hook",
    "version": "18.0.5.1.17",
}
