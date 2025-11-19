# Copyright 2025 Loym AS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "FIQ Documents",
    "summary": "",
    "author": "FIQ, Loym",
    "website": "https://github.com/OCA/knowledge",
    "version": "18.0.5.1.2",
    "license": "AGPL-3",
    "data": [
        "views/documents_document_views.xml",
        "views/res_partner_views.xml",
    ],
    "depends": [
        "base_fiq",
        # "documents_code", # First install documents_code
        "documents_form",
        "documents_name",
        "documents_tag",
        "documents_url",
        "partner_documents_folder",
    ],
}
