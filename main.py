import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import load_config, on_startup
from middlewares import DbSessionMiddleware
from handlers.command_router import router as command_router
from handlers.user_router import router as user_router
from handlers.faq_router import router as faq_router
from handlers.pickpoint_router import router as pickpoint_router
from handlers.siz_router import router as siz_router
from handlers.other_router import router as other_router
from services.notification import notification_job

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
    )

    logger.info('Starting bot')

    config = load_config()

    engine = create_async_engine(url=config.db.url, echo=True)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=config.bot.storage)

    dp.startup.register(on_startup)
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))

    dp.include_router(command_router)
    dp.include_router(user_router)
    dp.include_router(faq_router)
    dp.include_router(pickpoint_router)
    dp.include_router(siz_router)
    dp.include_router(other_router)

    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(
        notification_job,
        trigger='interval',
        minutes=10,
        kwargs={'bot': bot, 'session_maker': session_maker}
    )
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Stopping bot')
