# Copyright 2026 FIQ as
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "FIQ Mail – Communication inbox",
    "summary": "Outlook-style inbox: preview an incoming message and file it under the "
               "right Odoo element (project / sales order / opportunity) as a PDF with metadata.",
    "author": "FIQ as",
    "website": "https://fiq.no",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "category": "Productivity/FIQ",
    "depends": ["fiq_komm_match", "web"],
    "data": [
        "report/fiq_komm_inbox_report.xml",
        "views/fiq_komm_inbox_action.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "fiq_komm_inbox/static/src/**/*",
        ],
    },
    "installable": True,
    "application": True,
}
