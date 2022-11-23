from django import template
register = template.Library()

@register.filter
def mod(num, val):
    return num % val

@register.filter
def subtract(value, arg):
    return value - arg