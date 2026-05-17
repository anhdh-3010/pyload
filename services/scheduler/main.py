import asyncio
import logging

import core.models  # noqa: F401
from services.scheduler.service import SchedulerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    service = SchedulerService()
    logger.info("Scheduler service started")
    await service.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
