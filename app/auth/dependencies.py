from app.auth.oauth_manager import OAuthManager
from app.config.settings import get_settings

_oauth_manager: OAuthManager | None = None


def get_oauth_manager() -> OAuthManager:
    global _oauth_manager
    if _oauth_manager is None:
        _oauth_manager = OAuthManager(get_settings())
    return _oauth_manager
