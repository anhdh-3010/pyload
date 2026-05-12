import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Scheduler service skeleton started")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
