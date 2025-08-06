from odoo import models, fields


class Partner(models.Model):
    _inherit = "res.partner"

    def action_see_documents(self):
        action = super().action_see_documents()
        action["views"] = [(False, "list"), (False, "kanban")]
        return action
