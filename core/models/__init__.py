"""Import model modules so Alembic can discover SQLAlchemy metadata."""

from modules.accounts.domain import models as account_models  # noqa: F401
from modules.download_tasks.domain import models as download_task_models  # noqa: F401
from modules.outbox.domain import models as outbox_models  # noqa: F401
