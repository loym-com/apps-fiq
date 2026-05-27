from odoo import fields, models


class ProjectType(models.Model):
    _inherit = "project.type"

    properties_definition = fields.PropertiesDefinition("Properties Definition")
