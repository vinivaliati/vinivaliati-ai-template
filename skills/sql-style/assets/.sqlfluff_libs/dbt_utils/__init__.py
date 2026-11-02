"""Lint-only stand-ins for dbt_utils macros, so sqlfluff's jinja templater can parse models.

sqlfluff loads each module in this folder as a Jinja variable named after it. These
functions only render SQL of the same shape; dbt never runs them. Add one when a model
uses another dbt_utils macro.
"""


def generate_surrogate_key(field_list: list[str]) -> str:
    return "md5(" + " || ".join(field_list) + ")"
