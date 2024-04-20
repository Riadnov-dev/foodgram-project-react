from rest_framework.exceptions import ValidationError


def validate_pk(pk):
    try:
        return int(pk)
    except ValueError:
        raise ValidationError('Invalid ID format. ID must be an integer.')