# Copyright 2025 Loym AS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "FIQ Base",
    "summary": "",
    "author": "FIQ as, Loym AS, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/knowledge",
    "version": "18.0.1.0.1",
    "license": "AGPL-3",
    "data": [
        "views/ir_module_views.xml",
    ],
    "depends": [
        "base_unique_code",
        "document_url", # OCA/document (attachment url)
        "portal_user",
        "sequence_choice",
    ],
}
