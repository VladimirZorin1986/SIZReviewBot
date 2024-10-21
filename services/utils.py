from typing import Any, Callable, Optional
from contextlib import suppress
from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from services.models import TrackCallback


async def add_message_to_track(message: Message, state: FSMContext) -> None:
    data: dict[str, Any] = await state.get_data()
    track_list: list[int] | None = data.get('track_messages')
    if track_list:
        track_list.append(message.message_id)
    else:
        track_list = [message.message_id]
    await state.update_data(track_messages=track_list)


async def _get_msg_stack(state: FSMContext) -> list[Message]:
    data = await state.get_data()
    return data.get('track_messages')


async def erase_last_messages(state: FSMContext, msg_cnt_to_delete: int, bot: Bot, chat_id: int) -> None:
    msg_stack = await _get_msg_stack(state)
    with suppress(TelegramBadRequest):
        await bot.delete_messages(chat_id=chat_id, message_ids=msg_stack[-msg_cnt_to_delete:])


async def set_track_callback(callback: CallbackQuery, message: Message, state: FSMContext) -> None:
    await state.update_data(
        cb=TrackCallback(
            message=message,
            callback_data=callback.data
        )
    )


async def get_track_callback(state: FSMContext) -> TrackCallback | None:
    data = await state.get_data()
    track_cb = data.get('cb')
    if track_cb:
        return track_cb


async def update_track_callback(track_cb: TrackCallback, callback: CallbackQuery, state: FSMContext) -> None:
    track_cb.callback_data = callback.data
    await state.update_data(cb=track_cb)


async def _erase_track_messages(state: FSMContext, bot: Bot, chat_id: int) -> None:
    data: dict[str, Any] = await state.get_data()
    track_msgs = data.get('track_messages')
    if track_msgs:
        for msg_id in track_msgs:
            with suppress(TelegramBadRequest):
                await bot.delete_message(chat_id=chat_id, message_id=msg_id)


async def terminate_state_branch(message: Message, state: FSMContext, add_last: bool = True) -> None:
    if add_last:
        await add_message_to_track(message, state)
    await _erase_track_messages(state, message.bot, message.chat.id)
    await state.clear()


async def save_variable_in_state(
        state: FSMContext, variable: Any, var_name: str, convert_func: Optional[Callable]) -> None:
    data = await state.get_data()
    variable = variable if not convert_func else convert_func(variable)
    data[var_name] = variable
    await state.update_data(**data)


async def get_variable_from_state(state: FSMContext, var_name: str) -> Any:
    data = await state.get_data()
    return data.get(var_name)


async def get_variables_from_state(state: FSMContext, var_names: list[str]) -> list[Any]:
    data = await state.get_data()
    return [data.get(var) for var in var_names]


async def set_msg_track(state: FSMContext) -> None:
    data = await state.get_data()
    track_messages = data.get('track_messages') or {}
    await state.update_data(track_messages=track_messages)


async def set_state_msg_item(state: FSMContext, state_name: str) -> None:
    data = await state.get_data()
    if state_name not in data['track_messages']:
        data['track_messages'][state_name] = []
        await state.update_data(track_messages=data['track_messages'])


async def add_msg_to_track(state: FSMContext, message_id: int, state_name: str) -> None:
    data = await state.get_data()
    data['track_messages'][state_name].append(message_id)
    await state.update_data(track_messages=data['track_messages'])
