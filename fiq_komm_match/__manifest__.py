# Copyright 2026 FIQ as
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "FIQ Mail – Categorization engine",
    "summary": "Suggests the right Odoo element (project / sales order / opportunity / task) "
               "for an incoming message, from sender, human-simple rules and subject/body references.",
    "author": "FIQ as",
    "website": "https://fiq.no",
    "version": "19.0.1.1.0",
    "license": "AGPL-3",
    "category": "Productivity/FIQ",
    "depends": ["mail_fiq", "project"],
    "data": [
        "security/ir.model.access.csv",
        "views/fiq_komm_regel_views.xml",
    ],
    "installable": True,
}
