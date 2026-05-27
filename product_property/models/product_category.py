from copy import deepcopy

from odoo import models
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = ["property.mixin", "product.category"]

    _properties_definition_field = "product_properties_definition"
    _properties_parent_field = "parent_id"
    _properties_sync_context_key = "skip_product_properties_sync"

    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.parent_id:
                record.write(
                    {
                        "product_properties_definition": deepcopy(
                            record.parent_id.product_properties_definition or []
                        )
                    }
                )
        return records

    def write(self, vals):
        parent_field = self._properties_parent_field
        definition_field = self._properties_definition_field
        parent_changed = False
        changed_parent_categories = self.browse()

        if parent_field in vals:
            new_parent_id = vals[parent_field]
            changed_parent_categories = self.filtered(
                lambda category: category[parent_field].id != new_parent_id
            )
            parent_changed = bool(changed_parent_categories)

        if parent_changed:
            for category in changed_parent_categories:
                if (
                    category.child_id
                    and category[parent_field].id != new_parent_id
                ):
                    raise ValidationError(
                        self.env._(
                            "You cannot change the parent category of %(category)s because it has child categories.",
                            category=category.display_name,
                        )
                    )

            vals = dict(vals)
            vals.pop(definition_field, None)

        result = super().write(vals)

        if parent_changed:
            for category in changed_parent_categories:
                if category[parent_field]:
                    category.write(
                        {
                            definition_field: deepcopy(
                                category[parent_field].product_properties_definition or []
                            )
                        }
                    )

        return result
