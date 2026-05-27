from copy import deepcopy

from odoo import models
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = "product.category"

    def write(self, vals):
        should_sync = (
            "product_properties_definition" in vals
            and not self.env.context.get("skip_product_properties_sync")
        )
        previous_definitions_by_id = {
            category.id: deepcopy(category.product_properties_definition or [])
            for category in self
        }

        if should_sync:
            for category in self:
                self._validate_property_definition_update(
                    category,
                    previous_definitions_by_id.get(category.id, []),
                    vals.get("product_properties_definition") or [],
                )

        result = super().write(vals)

        if should_sync:
            for category in self:
                old_definitions = previous_definitions_by_id.get(category.id, [])
                new_definitions = deepcopy(category.product_properties_definition or [])
                added_definitions, removed_codes = self._get_definition_changes(
                    old_definitions, new_definitions
                )
                if not added_definitions and not removed_codes:
                    continue

                descendants = self.search(
                    [("id", "child_of", category.id), ("id", "!=", category.id)]
                )
                for child in descendants:
                    child_definitions = deepcopy(child.product_properties_definition or [])

                    if removed_codes:
                        child_definitions = [
                            definition
                            for definition in child_definitions
                            if definition.get("code") not in removed_codes
                        ]

                    existing_codes = {
                        definition.get("code")
                        for definition in child_definitions
                        if definition.get("code")
                    }
                    for definition in added_definitions:
                        code = definition.get("code")
                        if code and code not in existing_codes:
                            child_definitions.append(deepcopy(definition))
                            existing_codes.add(code)

                    if child_definitions != (child.product_properties_definition or []):
                        child.with_context(skip_product_properties_sync=True).write(
                            {"product_properties_definition": child_definitions}
                        )

        return result

    @staticmethod
    def _get_definition_changes(old_definitions, new_definitions):
        old_by_code = {
            definition.get("code"): definition
            for definition in old_definitions
            if definition.get("code") and definition.get("type") != "separator"
        }
        new_by_code = {
            definition.get("code"): definition
            for definition in new_definitions
            if definition.get("code") and definition.get("type") != "separator"
        }

        added_definitions = [
            deepcopy(new_by_code[code])
            for code in new_by_code
            if code not in old_by_code
        ]
        removed_codes = {code for code in old_by_code if code not in new_by_code}
        return added_definitions, removed_codes

    def _validate_property_definition_update(self, category, old_definitions, new_definitions):
        added_definitions, removed_codes = self._get_definition_changes(
            old_definitions, new_definitions
        )
        added_codes = {definition.get("code") for definition in added_definitions}
        added_codes.discard(None)

        parent_codes = self._get_category_codes(category.parent_id)
        if removed_codes and parent_codes:
            blocked_codes = sorted(code for code in removed_codes if code in parent_codes)
            if blocked_codes:
                raise ValidationError(
                    category.env._(
                        "You cannot delete property code(s) %(codes)s because the parent category uses them.",
                        codes=", ".join(blocked_codes),
                    )
                )

        changed_code_pairs = self._get_changed_code_pairs(
            old_definitions, new_definitions, added_codes, removed_codes
        )
        if not changed_code_pairs:
            return

        child_codes = self._get_descendant_codes(category)
        related_codes = parent_codes | child_codes

        for old_code, new_code in changed_code_pairs:
            if old_code in related_codes or new_code in related_codes:
                raise ValidationError(
                    category.env._(
                        "You cannot change property code %(old)s to %(new)s because a parent or child category uses one of these codes.",
                        old=old_code,
                        new=new_code,
                    )
                )

    @staticmethod
    def _get_changed_code_pairs(
        old_definitions, new_definitions, added_codes, removed_codes
    ):
        old_by_name = {
            definition.get("name"): definition.get("code")
            for definition in old_definitions
            if definition.get("name")
            and definition.get("code")
            and definition.get("type") != "separator"
        }
        new_by_name = {
            definition.get("name"): definition.get("code")
            for definition in new_definitions
            if definition.get("name")
            and definition.get("code")
            and definition.get("type") != "separator"
        }

        changed_pairs = []
        for name in set(old_by_name) & set(new_by_name):
            old_code = old_by_name[name]
            new_code = new_by_name[name]
            if old_code != new_code:
                changed_pairs.append((old_code, new_code))

        # Fallback for a single remove + single add where technical name is absent.
        if not changed_pairs and len(removed_codes) == 1 and len(added_codes) == 1:
            changed_pairs.append((next(iter(removed_codes)), next(iter(added_codes))))

        return changed_pairs

    @staticmethod
    def _get_category_codes(category):
        if not category:
            return set()
        return {
            definition.get("code")
            for definition in (category.product_properties_definition or [])
            if definition.get("code") and definition.get("type") != "separator"
        }

    def _get_descendant_codes(self, category):
        descendants = self.search([("id", "child_of", category.id), ("id", "!=", category.id)])
        codes = set()
        for descendant in descendants:
            codes |= self._get_category_codes(descendant)
        return codes
