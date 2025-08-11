from . import models

def post_init_hook(env):
    env["documents.tag"].search([])._set_tooltip_or_tooltip_translate()
