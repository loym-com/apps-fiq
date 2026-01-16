from odoo import api, fields, models

class ProjectTask(models.Model):
    _name = "project.task"
    _inherit = ["project.task", "code.list.mixin"]
