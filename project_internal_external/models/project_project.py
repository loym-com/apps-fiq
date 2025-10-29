from odoo import api, fields, models


class ProjectProject(models.Model):
    _name = "project.project"
    _inherit = ["project.project", "sequence.number.mixin"]

    internal_external = fields.Selection(
        string="Internal/External",
        selection=[("i", "Internal"), ("e", "External")]
    )
    company_id = fields.Many2one(
        default=lambda self: self.env.company,
    )
    sequence_sequence = fields.Char(
        help="Value from ir.sequence"
    )

    @api.constrains("company_id", "internal_external")
    def set_sequence_code(self):
        for rec in self:
            if not rec.sequence_sequence:
                rec.sequence_sequence = rec.sequence_code
            rec.sequence_code = rec.get_value_from_source(
                "ir.config_parameter", "project_internal_external.project_sequence_pattern"
            )

    def write(self, vals):
        vals = self.ondelete_sequence_code_delete_also_sequence_sequence(vals)
        super().write(vals)
        return True

    def ondelete_sequence_code_delete_also_sequence_sequence(self, vals):
        if "sequence_code" in vals and not vals.get("sequence_code"):
            vals["sequence_sequence"] = ""
        return vals
