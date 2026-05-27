from copy import deepcopy

from odoo import models
from odoo.exceptions import ValidationError


class PropertyDefinitionMixin(models.AbstractModel):
    _name = "property.definition.mixin"
    _description = "Property Definition Mixin"

    _properties_definition_field = None
    _properties_definition_parent_field = None
    _properties_sync_context_key = "skip_properties_sync"

    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            parent = self._get_parent(record)
            if parent:
                record.write(
                    {
                        self._properties_definition_field: deepcopy(
                            self._get_property_definitions(parent) or []
                        )
                    }
                )
        return records

    def write(self, vals):
        parent_field = self._properties_definition_parent_field
        definition_field = self._properties_definition_field
        parent_changed = False
        changed_parent_records = self.browse()

        if parent_field in vals:
            new_parent_id = vals[parent_field]
            changed_parent_records = self.filtered(
                lambda record: record[parent_field].id != new_parent_id
            )
            parent_changed = bool(changed_parent_records)

        if parent_changed:
            for record in changed_parent_records:
                if self._get_descendants(record):
                    raise ValidationError(
                        self.env._(
                            "You cannot change the parent of %(record)s because it has child records.",
                            record=record.display_name,
                        )
                    )

            vals = dict(vals)
            vals.pop(definition_field, None)

        should_sync = bool(
            definition_field
            and definition_field in vals
            and not self.env.context.get(self._properties_sync_context_key)
        )

        previous_definitions_by_id = {
            record.id: deepcopy(self._get_property_definitions(record) or [])
            for record in self
        }

        if should_sync:
            for record in self:
                self._validate_property_definition_update(
                    record,
                    previous_definitions_by_id.get(record.id, []),
                    vals.get(definition_field) or [],
                )

        result = super().write(vals)

        if parent_changed:
            for record in changed_parent_records:
                parent = self._get_parent(record)
                if parent:
                    record.write(
                        {
                            definition_field: deepcopy(
                                self._get_property_definitions(parent) or []
                            )
                        }
                    )

        if should_sync:
            for record in self:
                old_definitions = previous_definitions_by_id.get(record.id, [])
                new_definitions = deepcopy(self._get_property_definitions(record) or [])
                added_definitions, removed_codes = self._get_definition_changes(
                    old_definitions, new_definitions
                )
                if not added_definitions and not removed_codes:
                    continue

                descendants = self._get_descendants(record)
                for child in descendants:
                    child_definitions = deepcopy(self._get_property_definitions(child) or [])

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

                    if child_definitions != (self._get_property_definitions(child) or []):
                        child.with_context(**{self._properties_sync_context_key: True}).write(
                            {definition_field: child_definitions}
                        )

        return result

    def _validate_property_definition_update(self, record, old_definitions, new_definitions):
        added_definitions, removed_codes = self._get_definition_changes(
            old_definitions, new_definitions
        )
        added_codes = {definition.get("code") for definition in added_definitions}
        added_codes.discard(None)

        parent_codes = self._get_record_codes(self._get_parent(record))
        if removed_codes and parent_codes:
            blocked_codes = sorted(code for code in removed_codes if code in parent_codes)
            if blocked_codes:
                raise ValidationError(
                    self.env._(
                        "You cannot delete property code(s) %(codes)s because the parent record uses them.",
                        codes=", ".join(blocked_codes),
                    )
                )

        changed_code_pairs = self._get_changed_code_pairs(
            old_definitions, new_definitions, added_codes, removed_codes
        )
        if not changed_code_pairs:
            return

        related_codes = parent_codes | self._get_descendant_codes(record)
        for old_code, new_code in changed_code_pairs:
            if old_code in related_codes or new_code in related_codes:
                raise ValidationError(
                    self.env._(
                        "You cannot change property code '%(old)s' to '%(new)s' because a parent or child record uses one of these codes.",
                        old=old_code,
                        new=new_code,
                    )
                )

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

    @staticmethod
    def _get_changed_code_pairs(old_definitions, new_definitions, added_codes, removed_codes):
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

        if not changed_pairs and len(removed_codes) == 1 and len(added_codes) == 1:
            changed_pairs.append((next(iter(removed_codes)), next(iter(added_codes))))

        return changed_pairs

    def _get_parent(self, record):
        if not self._properties_definition_parent_field:
            return self.browse()
        return record[self._properties_definition_parent_field]

    def _get_descendants(self, record):
        return self.search([("id", "child_of", record.id), ("id", "!=", record.id)])

    def _get_record_codes(self, record):
        if not record:
            return set()
        return {
            definition.get("code")
            for definition in (self._get_property_definitions(record) or [])
            if definition.get("code") and definition.get("type") != "separator"
        }

    def _get_descendant_codes(self, record):
        codes = set()
        for descendant in self._get_descendants(record):
            codes |= self._get_record_codes(descendant)
        return codes

    def _get_property_definitions(self, record):
        return record[self._properties_definition_field] if self._properties_definition_field else []
