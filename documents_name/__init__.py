from . import models

def post_init_hook(env):
    for record in env["documents.document"].search([]):
        record.name_translate = record.name
