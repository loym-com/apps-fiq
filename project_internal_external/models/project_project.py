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

    # TODO: Replace constrains with create/write?

    @api.constrains("company_id", "internal_external")
    def set_sequence_code_sequence_number_and_name(self):
        self.sequence_number = None
        super().set_sequence_code_sequence_number_and_name()
