from . import models

def post_init_hook(env):
    env["documents.document"].search([])._set_tooltip_or_tooltip_translate()
