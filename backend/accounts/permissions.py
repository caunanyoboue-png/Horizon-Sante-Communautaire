from functools import wraps

from django.core.exceptions import PermissionDenied


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Priorité: group Django (approche robuste)
            if request.user.groups.filter(name__in=list(roles)).exists():
                return view_func(request, *args, **kwargs)

            # Fallback: profil.role
            profil = getattr(request.user, "profil", None)
            if profil is None or profil.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
