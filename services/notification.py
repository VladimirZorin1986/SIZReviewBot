from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from dao.user import UserDAO


class NotificationService:
    @classmethod
    async def send_mass_notification(cls, bot: Bot, text: str, session: AsyncSession):
        users = await UserDAO.get_all_bot_users(session)
        print(users)
        print(text)
        print(bot.id)
        for user in users:
            try:
                await bot.send_message(chat_id=user.tg_id, text=text)
            except Exception as e:
                print(f'Не удалось отправить сообщение пользователю {user.id}\nТекст исключения:\n{e}')



