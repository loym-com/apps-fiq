def post_init_hook(env):
    """Set default config parameter for project sequence pattern if not already set."""

    key = "project_internal_external.project_sequence_pattern"
    default_value = "P{r.internal_external}{r.sequence_sequence}"
    env['ir.config_parameter'].sudo().set_param(key, default_value)


def pre_uninstall_hook(env):
    """Remove the project sequence config parameter when uninstalling the module."""

    key = "project_internal_external.project_sequence_pattern"
    existing = env['ir.config_parameter'].sudo().get_param(key)
    if existing:
        env['ir.config_parameter'].sudo().delete_param(key)
