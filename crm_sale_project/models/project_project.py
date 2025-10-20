import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = "project.project"

