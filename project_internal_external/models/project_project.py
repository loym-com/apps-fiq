from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    internal_external = fields.Selection(
        string="Internal/External",
        selection=[("i", "Internal"), ("e", "External")]
    )
    company_id = fields.Many2one(
        default=lambda self: self.env.company,
    )

    @api.constrains("company_id", "internal_external")
    def set_sequence_code_unique_code_and_name(self):
        self.unique_code = None
        super().set_sequence_code_unique_code_and_name()
