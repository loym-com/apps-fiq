from odoo import api, fields, models


class ProjectRole(models.Model):
    _name = "project.role"
    _inherit = ["code.list.mixin", "project.role", ]
