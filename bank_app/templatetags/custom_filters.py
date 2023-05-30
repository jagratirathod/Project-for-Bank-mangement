from django import template

register = template.Library()


@register.filter
def mask_account_number(value):
    value_str = str(value)
    masked_value = "x" * (len(value_str) - 4) + value_str[-4:]
    return masked_value
