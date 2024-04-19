import re

from django.core.exceptions import ValidationError


def validate_color(value):
    value = value.lower()
    if re.match(r'^#[0-9a-fA-F]{3}$', value):
        value = '#' + ''.join([ch * 2 for ch in value[1:]])
    if not re.match(r'^#[0-9a-fA-F]{6}$', value):
        raise ValidationError(f'{value} is not a valid HEX color.')
    return value
