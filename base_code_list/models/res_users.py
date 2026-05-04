from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    tag_ids = fields.Many2many("res.users.tag", string="Tags")
