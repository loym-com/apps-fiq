import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _name = "project.project"
    _inherit = ["project.project", "sequence.number.mixin"]

    def _compute_name_from_settings(self):
        name = self.get_value_from_source("ir.config_parameter", "crm_sale_project.project_name_pattern")
        if name:
            self.name = name
        else:
            _logger.warning(f"Could not compute name for project {self.id}")
