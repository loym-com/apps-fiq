from odoo import models, fields, api


class DocumentsTag(models.Model):
    _inherit = "documents.tag"
    _order = "name"

    tooltip_translate = fields.Char(
        string="Tooltip.",
        translate=True,
    )
    parent_ids = fields.Many2many(
        'documents.tag',
        'documents_tag_hierarchy_rel',
        'child_id',
        'parent_id',
        string="Parent Tags"
    )
    child_ids = fields.Many2many(
        'documents.tag',
        'documents_tag_hierarchy_rel',
        'parent_id',
        'child_id',
        string="Children Tags"
    )
    all_child_ids = fields.Many2many(
        'documents.tag',
        compute='_compute_all_child_ids',
        string="All Children",
    )

    # TODO: Create a translate mixin based on documents_name/models/documents_document.py

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals = self._set_tooltip_or_tooltip_translate(vals)
        return super().create(vals_list)
    
    def write(self, vals):
        vals = self._set_tooltip_or_tooltip_translate(vals)
        return super().write(vals)
    
    def _set_tooltip_or_tooltip_translate(self, vals):
        if "tooltip_translate" in vals:
            vals["tooltip"] = vals["tooltip_translate"]
        elif "tooltip" in vals:
            vals["tooltip_translate"] = vals["tooltip"]
        return vals

    def _compute_all_child_ids(self):
        for tag in self:
            if not tag.id:
                tag.all_child_ids = self.env['documents.tag']
                continue

            query = """
                WITH RECURSIVE descendants AS (
                    SELECT child_id
                    FROM documents_tag_hierarchy_rel
                    WHERE parent_id = %s
                    UNION
                    SELECT r.child_id
                    FROM documents_tag_hierarchy_rel r
                    JOIN descendants d ON r.parent_id = d.child_id
                )
                SELECT child_id FROM descendants;
            """
            self.env.cr.execute(query, (tag.id,))
            child_ids = [row[0] for row in self.env.cr.fetchall()]
            tag.all_child_ids = self.env['documents.tag'].browse(child_ids)
