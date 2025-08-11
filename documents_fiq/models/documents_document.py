from odoo import models, fields


class DocumentsDocument(models.Model):
    _inherit = "documents.document"
    _order = "is_folder, name" # not working
