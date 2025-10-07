# Copyright 2025 Loym AS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "FIQ Base",
    "summary": "",
    "author": "FIQ as, Loym AS, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/knowledge",
    "version": "19.0.1.0.2",
    "license": "AGPL-3",
    "data": [
        "views/ir_module_views.xml",
    ],
    "depends": [
        "base_unique_code",
        "document_url", # OCA/document (attachment url)
        # "partner_assign_location",
        # "portal_user", # Cannot install fiq_base when portal_user is a dependency
        "sequence_choice",
    ],
}
