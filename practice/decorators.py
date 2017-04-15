from functools import wraps
from django.utils.translation import ugettext_lazy as _


def check_permission(permissions, field=None):
    """
    This is a check permission decorator.
    :param user: System User object
    :param permissions: List of permissions that need to be checked
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            print (field)
            if field:
                user = getattr(self, field, None)
            else:
                user = self
            if not user:
                raise PermissionError('No permissions')
            # print(user.__dict__)
            return fn(self, *args, **kwargs)
        return wrapper
    return decorator
    