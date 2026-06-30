from django.contrib.auth.models import Group

from .models import OperationLog


ROLE_NAMES = ['owner', 'editor', 'viewer']


def ensure_default_groups():
    for role in ROLE_NAMES:
        Group.objects.get_or_create(name=role)


def get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_operation(request, action, detail=''):
    user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
    return OperationLog.objects.create(
        user=user,
        action=action,
        detail=detail,
        ip_address=get_client_ip(request),
    )
