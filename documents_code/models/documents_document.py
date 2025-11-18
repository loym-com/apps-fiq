from odoo import models, fields, api


class DocumentsDocument(models.Model):
    _inherit = "documents.document"
    _sql_constraints = [
        (
            "unique_code",
            "UNIQUE(code)",
            "The code must be unique for each document or folder.",
        ),
    ]

    code = fields.Char(
        string="Code",
        help="Internal code to identify the document or folder",
    )

    @api.depends("code", "name")
    def _compute_display_name(self):
        super()._compute_display_name()
        for rec in self:
            code = rec.code or ""
            name = rec.name or ""
            if code:
                if name:
                    rec.display_name = f"{code} {name}"
                else:
                    rec.display_name = code
