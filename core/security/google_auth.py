from authlib.integrations.starlette_client import OAuth
from core.config import config

oauth = OAuth()

# Đăng ký dịch vụ Google OAuth
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
    client_id=config.google_client_id,
    client_secret=config.google_client_secret,
)
