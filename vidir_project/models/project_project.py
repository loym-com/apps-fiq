from odoo import _, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    properties = fields.Properties(
        "Properties",
        definition="type_id.properties_definition",
        copy=True,
    )

    def _get_report_properties(self):
        self.ensure_one()
        raw_properties = self.read(["properties"])[0].get("properties") or []
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
                0 if item["code"] == "top" else 1,
                item["code"] == "",
                item["code"].lower(),
                item["label"].lower(),
            ),
        )

    def _get_report_property_value(self, definition):
        property_type = definition.get("type")
        value = definition.get("value")

        if property_type == "boolean":
            return _("Yes") if value else _("No")

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
