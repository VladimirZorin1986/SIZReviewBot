import datetime as dt
import asyncio
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from dao.user import UserDAO
from dao.admin import AdminDAO
from exceptions.admin import InvalidNotificationError


async def notification_job(bot: Bot, session_maker: async_sessionmaker):
    async with session_maker() as session:
        notifications = await AdminDAO.get_new_notifications(session)
        for notification in notifications:
            try:
                users = await UserDAO.get_all_bot_users(session)
                for user in users:
                    try:
                        await bot.send_message(chat_id=user.tg_id, text=notification.notice_text)
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        print(f'Не удалось отправить сообщение пользователю {user.id}\nТекст исключения:\n{e}')
                        raise InvalidNotificationError
            except InvalidNotificationError:
                print(f'Не удалось отправить уведомление с id={notification.id}')
            else:
                await AdminDAO.update_object(session, notification.id, delivered_at=dt.datetime.now())


class NotificationService:
    @classmethod
    async def send_mass_notification(cls, bot: Bot, text: str, session: AsyncSession):
        users = await UserDAO.get_all_bot_users(session)
        for user in users:
            try:
                await bot.send_message(chat_id=user.tg_id, text=text)
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f'Не удалось отправить сообщение пользователю {user.id}\nТекст исключения:\n{e}')
                raise InvalidNotificationError

    @classmethod
    async def send_mass_admin_notification(cls, bot: Bot, session: AsyncSession):
        notifications = await AdminDAO.get_new_notifications(session)
        for notification in notifications:
            try:
                await cls.send_mass_notification(bot=bot, session=session, text=notification.notice_text)
            except InvalidNotificationError:
                print(f'Не удалось отправить уведомление с id={notification.id}')
            else:
                await AdminDAO.update_object(session, notification.id, delivered_at=dt.datetime.now())


