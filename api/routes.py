from enum import Enum

class Routes(str, Enum):
    AUTH_LOGIN = '/api/auth/login'
    AUTH_REGISTER = '/api/auth/register'
    AUTH_VERIFY = '/api/auth/verify'
    
    PROFILES = '/api/profiles/'
    PROFILES_ME = '/api/profiles/me'
    PROFILES_ITEM = '/api/profiles/{}'

    def __str__(self) -> str:
        return self.value
