from copy import deepcopy

from odoo import models
from odoo.exceptions import ValidationError


class PropertyMixin(models.AbstractModel):
    _name = "property.mixin"
    _description = "Property Mixin"

    _properties_definition_field = None
    _properties_parent_field = None
    _properties_field = None
    _properties_sync_context_key = "skip_properties_sync"
    _properties_top_code = "top"

    def write(self, vals):
        definition_field = self._properties_definition_field
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
        if not self._properties_parent_field:
            return self.browse()
        return record[self._properties_parent_field]

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

    def _get_report_properties(self):
        self.ensure_one()
        properties_field = self._properties_field
        if not properties_field:
            return []

        raw_properties = self.read([properties_field])[0].get(properties_field) or []
        formatted_properties = []

        for definition in raw_properties:
            if definition.get("type") == "separator":
                continue

            code = definition.get("code") or ""
            label = definition.get("string") or code
            value = self._get_report_property_value(definition)
            if value is None:
                continue

            formatted_properties.append(
                {
                    "code": code,
                    "label": label,
                    "value": value,
                }
            )

        return sorted(
            formatted_properties,
            key=lambda item: (
                0 if item["code"] == self._properties_top_code else 1,
                item["code"] == "",
                item["code"].lower(),
                item["label"].lower(),
            ),
        )

    def _get_report_property_value(self, definition):
        property_type = definition.get("type")
        value = definition.get("value")

        if property_type == "boolean":
            return self.env._("Yes") if value else self.env._("No")

        if not value:
            return None

        if property_type == "many2one":
            return value[1]

        if property_type == "many2many":
            return ", ".join(record[1] for record in value if len(record) > 1)

        if property_type in ("selection", "tags"):
            options = {
                option[0]: option[1:]
                for option in (definition.get(property_type) or [])
            }
            if property_type == "selection":
                selected = options.get(value)
                return selected[0] if selected else None

            tag_names = [options[tag][0] for tag in value if tag in options]
            return ", ".join(tag_names) if tag_names else None

        if isinstance(value, list):
            return ", ".join(str(item) for item in value)

        return str(value)
