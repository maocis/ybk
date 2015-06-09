from .views import user
from .login import login, check_login, logout, admin_required

__all__ = ['user',
           'login', 'login', 'check_login', 'logout', 'admin_required']
