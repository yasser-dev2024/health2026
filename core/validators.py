from urllib.parse import urlparse

from django.core.exceptions import ValidationError


def validate_safe_url(value):
    if not value:
        return

    if value.startswith('/') and not value.startswith('//'):
        return

    parsed = urlparse(value)
    if parsed.scheme in {'https', 'tel'}:
        return

    raise ValidationError('يسمح فقط بالروابط الداخلية أو HTTPS أو tel:.')
