# Copyright 2026 FIQ
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class CodeListMixin(models.AbstractModel):
    _name = "code.list.mixin"
    _description = "Code List Mixin"

    code_list_usage_ids = fields.One2many(
        comodel_name="code.list.usage",
        inverse_name="res_id",
        domain=lambda self: [("model", "=", self._name)],
        copy=True,
    )
    code_list_item_ids = fields.Many2many(
        comodel_name="code.list.item",
        compute="_compute_code_list_item_ids",
        string="Code List Items",
    )
    @api.depends("code_list_usage_ids.code_list_item_id")
    def _compute_code_list_item_ids(self):
        for record in self:
            record.code_list_item_ids = record.code_list_usage_ids.mapped(
                "code_list_item_id"
            )
