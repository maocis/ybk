from .views import user
from .login import login, check_login, logout, admin_required
from .position import position, position_buy, position_sell
from .accounts import accounts
from .password import change_password

__all__ = ['user',
           'login', 'login', 'check_login', 'logout', 'admin_required',
           'position', 'position_buy', 'position_sell',
           'accounts',
           'change_password']
