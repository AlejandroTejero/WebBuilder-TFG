"""
Template tags y filtros personalizados para WebBuilder.
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Permite acceder a un dict con variable: {{ dict|get_item:key }}"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, "")
    return ""


@register.filter
def split(value, separator=","):
    """Divide un string por el separador: {{ "a,b,c"|split:"," }}"""
    return value.split(separator)
