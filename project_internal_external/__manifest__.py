# Copyright 2025 Loym
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Internal/External Projects",
    "summary": "",
    "author": "FIQ, Loym",
    "data": [
        "views/project_project_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "depends": [
        "project_sequence_number",
    ],
    "excludes": [""],
    "license": "LGPL-3",
    "version": "18.0.6.0.0",
    "website": "https://www.loym.com",
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "pre_uninstall_hook",
}
