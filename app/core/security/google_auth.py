from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
from app.core.config import config

oauth = OAuth()

# Đăng ký dịch vụ Google OAuth
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    },
    client_id=config.google_client_id,
    client_secret_key=config.google_client_secret,
)

# --- Cấu hình JWT (python-jose) ---
# Dependency để lấy token từ header "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/callback")
