from . import ast as templ_ast
from . import loc as templ_loc
from typing import Dict, Any


class Env(dict):
    @classmethod
    def empty(cls):
        return cls()


def parse(source):
    return templ_ast.mk_text("", templ_loc.DUMMY)


def eval_template(template, context):
    return ""


def render(template_string, context):
    template = parse(template_string)
    return eval_template(template, context)


def output_simple(conf: Any, env: Env, template_name: str):
    raise NotImplementedError("Template rendering not yet implemented")
