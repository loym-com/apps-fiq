# Copyright 2025 Loym AS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "FIQ Base",
    "summary": "",
    "author": "FIQ, Loym",
    "website": "https://github.com/OCA/knowledge",
    "version": "18.0.5.1.0",
    "license": "AGPL-3",
    "data": [
        "views/ir_module_views.xml",
    ],
    "depends": [
        "partner_sequence_number",
        "document_url", # OCA/document (attachment url)
        # "partner_assign_location",
        # "portal_user", # Cannot install fiq_base when portal_user is a dependency
    ],
}
